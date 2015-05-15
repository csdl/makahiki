'''Helper functions for the Smart Grid Game Library and grid instance.
Created on Mar 15, 2013

@author: Carleton Moore
'''

from django.db.models.deletion import Collector
from django.db.models.fields.related import ForeignKey
from apps.widgets.smartgrid.models import Action, Activity, Commitment, Event, Filler, ColumnName, \
    Level, TextPromptQuestion, Grid, ColumnGrid
from django.shortcuts import get_object_or_404
from apps.widgets.smartgrid_library.models import LibraryAction, LibraryActivity, \
    LibraryCommitment, LibraryEvent, LibraryColumnName, LibraryTextPromptQuestion
from django.http import Http404
from apps.widgets.smartgrid_design.models import DesignerAction, DesignerColumnName, \
    DesignerActivity, DesignerCommitment, DesignerEvent, DesignerFiller, DesignerLevel,\
    DesignerTextPromptQuestion, DesignerGrid, DesignerColumnGrid, Draft
import os
from django.core.management import call_command
from apps.managers.predicate_mgr import predicate_mgr
from django.conf import settings


def duplicate(obj, value=None, field=None, duplicate_order=None):  # pylint: disable=R0914
    """
    Duplicate all related objects of obj setting
    field to value. If one of the duplicate
    objects has an FK to another duplicate object
    update that as well. Return the duplicate copy
    of obj.
    duplicate_order is a list of models which specify how
    the duplicate objects are saved. For complex objects
    this can matter. Check to save if objects are being
    saved correctly and if not just pass in related objects
    in the order that they should be saved.
    """
    collector = Collector({})
    collector.collect([obj])
    collector.sort()
    related_models = collector.data.keys()
    data_snapshot = {}
    for key in collector.data.keys():
        data_snapshot.update({key: dict(zip([item.pk for item in collector.data[key]], \
                                            [item for item in collector.data[key]]))})
    root_obj = None

    # Sometimes it's good enough just to save in reverse deletion order.
    if duplicate_order is None:
        duplicate_order = reversed(related_models)

    for model in duplicate_order:

        # Find all FKs on model that point to a related_model.
        fks = []
        for f in model._meta.fields:
            if isinstance(f, ForeignKey) and f.rel.to in related_models:
                fks.append(f)
        # Replace each `sub_obj` with a duplicate.
        if model not in collector.data:
            continue
        sub_objects = collector.data[model]
        for obj in sub_objects:
            for fk in fks:
                fk_value = getattr(obj, "%s_id" % fk.name)
                # If this FK has been duplicated then point to the duplicate.
                fk_rel_to = data_snapshot[fk.rel.to]
                if fk_value in fk_rel_to:
                    dupe_obj = fk_rel_to[fk_value]
                    setattr(obj, fk.name, dupe_obj)
            # Duplicate the object and save it.
            obj.id = None
            if field is None or field != 'slug':
                slug = obj.slug
                obj.slug = slug + '-copy'
            if field is not None:
                setattr(obj, field, value)
            obj.save()
            if root_obj is None:
                root_obj = obj
    return root_obj
# pylint: enable=R0914


def check_designer_vs_library(draft):
    """Checks the slugs in the designer vs the library. Returns
list of slugs in designer not in library."""
    l = []
    for des_action in DesignerAction.objects.filter(draft=draft):
        slug = des_action.slug
        try:
            get_library_action(slug)
        except Http404:
            l.append(slug)
    return l


def is_library(obj):
    """Returns True if the object is a Library instance."""
    cls = type(obj).__name__
    return cls.startswith('Library')


def is_designer(obj):
    """Returns True if the object is a Designer instance."""
    cls = type(obj).__name__
    return cls.startswith('Designer')


def is_smartgrid(obj):
    """Returns True if the object is a SmartGrid instance."""
    return not (is_library(obj) or is_designer(obj))


def _copy_fields(orig, copy):
    """Copies the field values from orig to copy and saves the copy."""
    for f in orig._meta.fields:
        if f.name != 'id':
            value = getattr(orig, f.name)
            setattr(copy, f.name, value)
    copy.save()


def _copy_fields_no_foriegn_keys(orig, copy):
    """Copies the field values from orig to copy and saves the copy."""
    fks = []
    for f in orig._meta.fields:
        if isinstance(f, ForeignKey):
            fks.append(f.name)
#    print fks
    for f in orig._meta.fields:
        if f.name != 'id' and not f.name in fks:
            value = getattr(orig, f.name)
            setattr(copy, f.name, value)


def _admin_link(action):
    """returns the hardcoded link to edit the action."""
    return "<a href='/challenge_setting_admin/smartgrid_design/designer%s/%s/'>%s</a>" % \
        (action.type, action.pk, action.name)


def __slug_has_copy_num(slug):
    """Returns True if the given slug has a copy number.  Copy numbers are defined as slug-#."""
    parts = slug.split('-')
    last = parts[len(parts) - 1]
    return last.isdigit()


def __get_copy_num(slug):
    """Returns the number at the end of the given slug (e.g. intro-video returns -1,
    play-outside-cafe-1 returns 1."""
    parts = slug.split('-')
    last = parts[len(parts) - 1]
    if last.isdigit():
        return int(last)
    else:
        return -1


def __get_slug_wo_copy_num(slug):
    """Returns the slug prefix without the copy number. For slugs without copy numbers returns
    the slug-."""
    if __slug_has_copy_num(slug):
        return slug[: slug.rfind('-') + 1]
    else:
        return "%s-" % slug


def __get_next_library_copy_slug(slug):
    """Returns the next available copy slug. Copy slugs have the copy_num appended to the slug
    prefix."""
    copy_num = __get_copy_num(slug)
    slug_prefix = __get_slug_wo_copy_num(slug)
    done = False
    while not done:
        try:
            copy_num += 1
            get_library_action('%s%d' % (slug_prefix, copy_num))
        except Http404:
            done = True
    return '%s%d' % (slug_prefix, copy_num)


def __get_next_designer_copy_slug(draft, slug):
    """Returns the next available copy slug. Copy slugs have the copy_num appended to the slug
    prefix."""
    copy_num = __get_copy_num(slug)
    slug_prefix = __get_slug_wo_copy_num(slug)
    done = False
    while not done:
        try:
            copy_num += 1
            get_designer_action(draft, '%s%d' % (slug_prefix, copy_num))
        except Http404:
            done = True
    return '%s%d' % (slug_prefix, copy_num)


def instantiate_designer_column_from_library(draft, slug):
    """Instantiates a DesignerColumnName from the LibraryColumnName with the given draft and
    slug."""
    lib_cat = get_object_or_404(LibraryColumnName, slug=slug)
    des_col = None
    try:
        des_col = get_object_or_404(DesignerColumnName, draft=draft, slug=slug)
    except Http404:
        des_col = DesignerColumnName()
        des_col.draft = draft
    _copy_fields(lib_cat, des_col)
    return des_col


def instantiate_designer_action_from_library(draft, slug):
    """Instantiates a Smart Grid Game Design instance from the Smart Grid Game Library instance.
    draft is the draft to use. slug is the slug value for the library instance. If the Design
    instance exists it is over written."""
    lib_obj = get_library_action(slug)
    action_type = lib_obj.type
    exist_obj = None
    try:
        exist_obj = get_designer_action(draft, slug)
    except Http404:
        exist_obj = None
    design_obj = None
    if exist_obj == None:
        if action_type == 'activity':
            design_obj = DesignerActivity()
            lib_obj = LibraryActivity.objects.get(slug=slug)
        if action_type == 'commitment':
            design_obj = DesignerCommitment()
            lib_obj = LibraryCommitment.objects.get(slug=slug)
        if action_type == 'event':
            design_obj = DesignerEvent()
            lib_obj = LibraryEvent.objects.get(slug=slug)
        if action_type == 'filler':
            design_obj = DesignerFiller()
        design_obj.draft = draft
    else:  # use the existing instance.
        design_obj = exist_obj

    _copy_fields(lib_obj, design_obj)

    # Copy all the LibraryTextPropmtQuestions
    for question in LibraryTextPromptQuestion.objects.filter(libraryaction=lib_obj):
        try:
            des_obj = get_object_or_404(DesignerTextPromptQuestion, action=design_obj, \
                                        question=question.question, answer=question.answer, \
                                        draft=draft)
        except Http404:
            des_obj = DesignerTextPromptQuestion()
        _copy_fields_no_foriegn_keys(question, des_obj)
        des_obj.action = get_designer_action(draft, slug)
        des_obj.draft = draft
        des_obj.save()

    return design_obj


def instantiate_designer_level_from_smartgrid(draft, slug):
    """Creates or over writes a DesignerLevel for the given designer draft and level slug."""
    level = get_object_or_404(Level, slug=slug)
    try:
        des_level = get_object_or_404(DesignerLevel, draft=draft, slug=slug)
    except Http404:
        des_level = DesignerLevel()
        des_level.draft = draft
    _copy_fields(level, des_level)

    return des_level


def instantiate_designer_column_from_smartgrid(draft, slug):
    """Creates a DesignerColumnName from the ColumnName with the given slug."""
    col = get_object_or_404(ColumnName, slug=slug)
    des_col = None
    try:
        des_col = get_object_or_404(DesignerColumnName, draft=draft, slug=slug)
    except Http404:
        des_col = DesignerColumnName()
        des_col.draft = draft
    _copy_fields(col, des_col)
    return des_col


def instantiate_designer_action_from_smartgrid(draft, slug):
    """Creates a designer instance from the Smart Grid instance with the given draft."""
    grid_obj = get_smartgrid_action(slug)
    action_type = grid_obj.type
    old_obj = None
    try:
        old_obj = get_designer_action(draft, slug)
    except Http404:
        old_obj = None
    designer_obj = None
    if old_obj == None:
        if action_type == 'activity':
            designer_obj = DesignerActivity()
        if action_type == 'commitment':
            designer_obj = DesignerCommitment()
        if action_type == 'event':
            designer_obj = DesignerEvent()
        if action_type == 'filler':
            designer_obj = DesignerFiller()
        designer_obj.draft = draft
    else:
        designer_obj = old_obj
    _copy_fields(grid_obj, designer_obj)

    # Copy all the TextPropmtQuestions
    for question in TextPromptQuestion.objects.filter(action=grid_obj):
        try:
            des_obj = get_object_or_404(DesignerTextPromptQuestion, action=designer_obj, \
                                        question=question.question, answer=question.answer, \
                                        draft=draft)
        except Http404:
            des_obj = DesignerTextPromptQuestion()
        _copy_fields_no_foriegn_keys(question, des_obj)
        des_obj.action = get_designer_action(draft, slug)
        des_obj.draft = draft
        des_obj.save()

    return designer_obj


def instantiate_smartgrid_level_from_designer(des_level):
    """Creates a Smart Grid Level from the DesignerLevel."""
    level = None
    try:
        level = get_smartgrid_level(des_level.slug)
    except Http404:
        level = Level()
    _copy_fields(des_level, level)
    return level


def instantiate_smartgrid_column_from_designer(des_col):
    """Creates a Smart Grid ColumnName from the DesignerColumnName."""
    col = None
    try:
        col = get_smartgrid_column_name(des_col.slug)
    except Http404:
        col = ColumnName()
    _copy_fields(des_col, col)
    return col


def instantiate_smartgrid_action_from_designer(draft, slug):
    """Creates a Smart Grid instance from the designer instance."""
    des_action = get_designer_action(draft, slug)
    action_type = des_action.type
    old_obj = None
    try:
        old_obj = get_smartgrid_action(slug)
    except Http404:
        old_obj = None
    grid_action = None
    if old_obj == None:
        if action_type == 'activity':
            grid_action = Activity()
        if action_type == 'commitment':
            grid_action = Commitment()
        if action_type == 'event':
            grid_action = Event()
        if action_type == 'filler':
            grid_action = Filler()
    else:
        grid_action = old_obj
    _copy_fields_no_foriegn_keys(des_action, grid_action)
    grid_action.save()

    # Copy all the DesignerTextPropmtQuestions
    for question in DesignerTextPromptQuestion.objects.filter(draft=draft, action=des_action):
        old_ques = TextPromptQuestion.objects.filter(action=grid_action, \
                                                     question=question.question, \
                                                     answer=question.answer)
        if len(old_ques) == 0:
            tqp = TextPromptQuestion(action=grid_action, question=question.question, \
                                     answer=question.answer)
            tqp.save()

    return grid_action


def copy_library_action(slug):
    """Copies the LibraryAction with the given slug."""
    action = get_library_action(slug)
    action_type = action.type
    if action_type == 'activity':
        obj = LibraryActivity()
    elif action_type == 'commitment':
        obj = LibraryCommitment()
    elif action_type == 'event':
        obj = LibraryEvent()
    _copy_fields(action, obj)
    copy_slug = __get_next_library_copy_slug(slug)
    obj.slug = copy_slug
    obj.pk = None
    obj.id = None
    obj.save()
    # Copy all the LibraryTextPropmtQuestions
    for question in LibraryTextPromptQuestion.objects.filter(libraryaction=action):
        try:
            des_obj = get_object_or_404(LibraryTextPromptQuestion, action=obj, \
                                        question=question.question, answer=question.answer)
        except Http404:
            des_obj = LibraryTextPromptQuestion()
        _copy_fields_no_foriegn_keys(question, des_obj)
        des_obj.action = obj
        des_obj.save()

    return obj


def copy_draft(from_draft, to_draft):
    """Copies all the items in from_draft to copy_draft."""
#     print "copy_draft(%s, %s)" % (from_draft, to_draft)
    clear_designer(to_draft)
    # levels
    for level in DesignerLevel.objects.filter(draft=from_draft):
        copy = DesignerLevel(draft=to_draft)
        _copy_fields_no_foriegn_keys(level, copy)
        copy.save()
    # ColumnNames
    for column in DesignerColumnName.objects.filter(draft=from_draft):
        copy = DesignerColumnName(draft=to_draft)
        _copy_fields_no_foriegn_keys(column, copy)
        copy.save()
    # DesignerColumnGrid
    for loc in DesignerColumnGrid.objects.filter(draft=from_draft):
        level = get_designer_level(to_draft, loc.level.slug)
        column = get_designer_column_name(to_draft, loc.name.slug)
        copy = DesignerColumnGrid(draft=to_draft, name=column, level=level)
        _copy_fields_no_foriegn_keys(loc, copy)
        copy.save()
    # DesignerActions
    for action in DesignerAction.objects.filter(draft=from_draft):
        action = get_designer_action(from_draft, action.slug)
        if action.type == 'activity':
            copy = DesignerActivity(draft=to_draft)
        elif action.type == 'commitment':
            copy = DesignerCommitment(draft=to_draft)
        elif action.type == 'event':
            copy = DesignerEvent(draft=to_draft)
        _copy_fields_no_foriegn_keys(action, copy)
        copy.save()
        # Copy all the DesignerTextPropmtQuestions
        for question in DesignerTextPromptQuestion.objects.filter(action=action, draft=from_draft):
            des_obj = DesignerTextPromptQuestion(action=copy, draft=to_draft)
            _copy_fields_no_foriegn_keys(question, des_obj)
            des_obj.save()
    # DesignerGrid
    for loc in DesignerGrid.objects.filter(draft=from_draft):
        level = get_designer_level(to_draft, loc.level.slug)
        action = get_designer_action(to_draft, loc.action.slug)
        copy = DesignerGrid(level=level, draft=to_draft, action=action)
        _copy_fields_no_foriegn_keys(loc, copy)
        copy.save()
    return to_draft


def copy_designer_action(draft, slug):
    """Copies the DesignerAction with the given slug."""
    action = get_designer_action(draft, slug)
    action_type = action.type
    if action_type == 'activity':
        obj = DesignerActivity()
    elif action_type == 'commitment':
        obj = DesignerCommitment()
    elif action_type == 'event':
        obj = DesignerEvent()
    _copy_fields(action, obj)
    copy_slug = __get_next_designer_copy_slug(draft, slug)
    obj.slug = copy_slug
    obj.pk = None
    obj.id = None
    obj.save()
    # Copy all the DesignerTextPropmtQuestions
    for question in DesignerTextPromptQuestion.objects.filter(action=action, draft=draft):
        des_obj = DesignerTextPromptQuestion()
        _copy_fields_no_foriegn_keys(question, des_obj)
        des_obj.action = obj
        des_obj.draft = draft
        des_obj.save()

    return obj


def get_designer_action(draft, slug):
    """Returns the Smart Grid Game Designer Action for the given draft and slug or throws
    Http404 exception if the DesignerAction doesn't exist."""
    action = get_object_or_404(DesignerAction, draft=draft, slug=slug)
    if action.type == 'activity':
        return DesignerActivity.objects.get(draft=draft, slug=slug)
    if action.type == 'commitment':
        return DesignerCommitment.objects.get(draft=draft, slug=slug)
    if action.type == 'event':
        return DesignerEvent.objects.get(draft=draft, slug=slug)
    if action.type == 'filler':
        return DesignerFiller.objects.get(draft=draft, slug=slug)
    return action


def get_designer_action_slugs(draft):
    """Returns the DesignerAction slugs that are currently in the Smart Grid Designer
    for the given draft. This includes the actions in the palette."""
    action_list = []
    for action in DesignerAction.objects.filter(draft=draft):
        action_list.append(action.slug)
    return action_list


def get_designer_column_name(draft, slug):
    """Return the Smart Grid Game DesignerColumnName for the given slug."""
    return get_object_or_404(DesignerColumnName, draft=draft, slug=slug)


def get_designer_column_name_slugs(draft):
    """Returns the DesignerColumnName slugs that are currently in the Smart Grid Designer."""
    slugs = []
    for col in DesignerColumnGrid.objects.filter(draft=draft):
        slugs.append(col.name.slug)
    return slugs


def get_designer_draft(slug):
    """Returns the Draft for the given slug or Http404 exception."""
    return get_object_or_404(Draft, slug=slug)


def get_designer_level(draft, slug):
    """Return the DesignerLevel for the given slug."""
    return get_object_or_404(DesignerLevel, draft=draft, slug=slug)


def get_designer_levels(draft):
    """Return a list of the DesignerLevels for the given draft."""
    return DesignerLevel.objects.filter(draft=draft)


def get_designer_test_levels(draft, user):
    """Returns a list of DesignerLevels with their unlock conditions set according to the
    test predicates."""
    levels = []
    for level in Level.objects.all():
        level.is_unlock = predicate_mgr.eval_play_tester_predicates(level.unlock_condition,
                                                                    user, draft)
        levels.append(level)
    return levels


def get_library_action(slug):
    """Returns the Smart Grid Game Library Action for the given slug."""
    action = get_object_or_404(LibraryAction, slug=slug)
    if action.type == 'activity':
        return LibraryActivity.objects.get(slug=slug)
    if action.type == 'commitment':
        return LibraryCommitment.objects.get(slug=slug)
    if action.type == 'event':
        return LibraryEvent.objects.get(slug=slug)
    return action


def get_library_column_name(slug):
    """Return the Smart Grid Game LibraryColumnName for the given slug."""
    return get_object_or_404(LibraryColumnName, slug=slug)


def get_smartgrid_action(slug):
    """returns the action object by slug."""
    action = get_object_or_404(Action, slug=slug)
    if action.type == 'activity':
        return Activity.objects.get(slug=slug)
    if action.type == 'commitment':
        return Commitment.objects.get(slug=slug)
    if action.type == 'event':
        return Event.objects.get(slug=slug)
    if action.type == 'filler':
        return Filler.objects.get(slug=slug)
    return action


def get_smartgrid_action_slugs():
    """Returns the Actions that are currently in the Smart Grid."""
    action_list = []
    for grid in Grid.objects.all():
        if grid.action.slug not in action_list:
            action_list.append(grid.action.slug)
    return action_list


def get_smartgrid_column_name(slug):
    """returns the ColumnName object by slug."""
    return get_object_or_404(ColumnName, slug=slug)


def get_smartgrid_level(slug):
    """Returns the Level for the given slug."""
    return get_object_or_404(Level, slug=slug)


def get_smartgrid():
    """Returns the currently defined smart grid."""
    levels = []
    return levels


def get_designer_grid(draft):
    """Returns the smart grid as defined in the Smart Grid Designer. The
    grid is a list of lists with the format [<DesignerLevel>, [<DesignerColumnName>*],
    [<DesignerAction>*], [active columns]"""
    ret = []
    for level in DesignerLevel.objects.filter(draft=draft):
        level_ret = []
        level_ret.append(level)
        level_ret.append(DesignerColumnGrid.objects.filter(draft=draft, level=level))
        level_ret.append(DesignerGrid.objects.filter(draft=draft, level=level))
        columns = []
        for cat in level_ret[1]:
            if cat.column not in columns:
                columns.append(cat.column)
        for act in level_ret[2]:
            if act.column not in columns:
                columns.append(act.column)
        level_ret.append(columns)
        ret.append(level_ret)
    return ret


def get_designer_palette(draft):
    """Returns the DesignerActions with no Level or no Column.  These actions will not
    appear in the grid if published."""
    palette = []
    for action in DesignerAction.objects.filter(draft=draft):
        if len(DesignerGrid.objects.filter(action=action)) == 0:
            palette.append(action)
    return palette


def clear_designer(draft):
    """Deletes all the instances in the designer draft. Only do this rarely."""
#     print "clear_designer(%s)" % draft
    for obj in DesignerLevel.objects.filter(draft=draft):
        obj.delete()
    for obj in DesignerColumnName.objects.filter(draft=draft):
        obj.delete()
    for obj in DesignerAction.objects.filter(draft=draft):
        obj.delete()
    for obj in DesignerColumnGrid.objects.filter(draft=draft):
        obj.delete()
    for obj in DesignerGrid.objects.filter(draft=draft):
        obj.delete()


def __clear_drafts():
    """Deletes all the Drafts and their objects. This includes the Draft 'None'."""
    for draft in Draft.objects.all():
        draft.delete()
    clear_designer(draft=None)


def copy_smartgrid_to_designer(draft):
    """Copies the current Smart Grid Game to the given designer draft."""
    # Clear out the Designer
    clear_designer(draft)
    # Copy the levels
    for lvl in Level.objects.all():
        try:
            des_lvl = get_object_or_404(DesignerLevel, draft=draft, slug=lvl.slug)
        except Http404:
            des_lvl = DesignerLevel()
            des_lvl.draft = draft
        _copy_fields(lvl, des_lvl)
    # Copy the ColumnNames
    for col in ColumnName.objects.all():
        try:
            des_col = get_object_or_404(DesignerColumnName, draft=draft, slug=col.slug)
        except Http404:
            des_col = DesignerColumnName()
            des_col.draft = draft
        _copy_fields(col, des_col)
    # Copy the location information
    for grid in ColumnGrid.objects.all():
        col = DesignerColumnGrid()
        col.level = get_designer_level(draft, grid.level.slug)
        col.column = grid.column
        col.name = get_designer_column_name(draft, grid.name.slug)
        col.draft = draft
        col.save()
    # Copy the Actions
    for action in Action.objects.all():
        instantiate_designer_action_from_smartgrid(draft, action.slug)
    # Copy the location information
    for grid in Grid.objects.all():
        loc = DesignerGrid()
        loc.level = get_designer_level(draft, grid.level.slug)
        loc.column = grid.column
        loc.row = grid.row
        loc.action = get_designer_action(draft, grid.action.slug)
        loc.draft = draft
        loc.save()


def clear_smartgrid():
    """Removes all the location information for the Smart Grid.
    Deletes the existing levels.  Does not affect the Smart Grid Actions."""
    for level in Level.objects.all():
        level.delete()
    for col in ColumnName.objects.all():
        col.delete()
    for row in ColumnGrid.objects.all():
        row.delete()
    for row in Grid.objects.all():
        row.delete()


def deploy_designer_to_smartgrid(draft, use_filler):  # pylint: disable=R0914
    """Clears the current Smart Grid Game and copies the designer instances to the
    Smart Grid Game. Clearing the grid does not delete the actions just clears their
    Levels and Categories."""
    clear_smartgrid()
    # deploy the Levels
    for level in DesignerLevel.objects.filter(draft=draft):
        instantiate_smartgrid_level_from_designer(level)
    # deploy the ColumnNames
    for col in DesignerColumnName.objects.filter(draft=draft):
        instantiate_smartgrid_column_from_designer(col)
    # set the ColumnGrid objects.
    for des_col in DesignerColumnGrid.objects.filter(draft=draft):
        col = ColumnGrid()
        col.column = des_col.column
        col.level = get_smartgrid_level(des_col.level.slug)
        col.name = get_smartgrid_column_name(des_col.name.slug)
        col.save()
    # set the Grid objects.
    for des_row in DesignerGrid.objects.filter(draft=draft):
        row = Grid()
        row.row = des_row.row
        row.column = des_row.column
        row.level = get_smartgrid_level(des_row.level.slug)
        instantiate_smartgrid_action_from_designer(draft, des_row.action.slug)
        row.action = get_smartgrid_action(des_row.action.slug)
        row.save()
    if use_filler:
        # need to instantiate the filler objects and put them in the grid.
        filler_count = len(Filler.objects.all())
        sizes = get_smart_grid_size()
        for slug in list(sizes):
            level = Level.objects.get(slug=slug)
            for c in range(1, sizes[slug][0] + 1):
                for r in range(1, sizes[slug][1] + 1):
                    cell = Grid.objects.filter(level=level, column=c, row=r)
                    if not cell:
                        filler_count += 1
                        name = 'Filler %s' % filler_count
                        filler_slug = 'filler-%s' % filler_count
                        filler = Filler(name=name, slug=filler_slug, type='filler', title=name)
                        filler.save()
                        grid = Grid(level=level, column=c, row=r, action=filler)
                        grid.save()  # pylint: enable=R0914


def get_smart_grid_size():
    """Returns the maximum columns and rows for each level in the smartgrid as a dictionary with
    the keys being the level slug and values being [num_column, num_row]."""
    ret = {}
    for level in Level.objects.all():
        num_column = 0
        for grid in ColumnGrid.objects.filter(level=level):
            if grid.column > num_column:
                num_column = grid.column
        num_row = 0
        for grid in Grid.objects.filter(level=level):
            if grid.column > num_column:
                num_column = grid.column
            if grid.row > num_row:
                num_row = grid.row
        ret[level.slug] = [num_column, num_row]

    return ret


def is_diff_between_designer_and_grid_action(draft, action_slug):
    """Returns True if there is a difference between the Designer Action and
    Grid Action with the given slug."""
    grid = get_smartgrid_action(action_slug)
    fks = []
    for f in grid._meta.fields:
        if isinstance(f, ForeignKey):
            fks.append(f.name)
    designer = get_designer_action(draft, action_slug)
    for f in grid._meta.fields:
        if f.name in fks:
            if not f.name.endswith('_ptr'):
                grid_val = getattr(grid, f.name).name
                designer_val = getattr(designer, f.name).name
                if grid_val != designer_val:
                    return True
        elif f.name != 'id':
            grid_val = getattr(grid, f.name)
            designer_val = getattr(designer, f.name)
            if grid_val != designer_val:
                return True
    return False


def diff_between_designer_and_grid_action(draft, action_slug):  # pylint: disable=R0912
    """Returns a list of the fields that are different between the Designer Action and
    Grid Action with the given slug."""
    grid = None
    designer = None
    t = 'action'
    try:
        designer = get_designer_action(draft, action_slug)
        t = designer.type
        grid = get_smartgrid_action(action_slug)
        t = grid.type
        fks = []
        for f in grid._meta.fields:
            if isinstance(f, ForeignKey):
                fks.append(f.name)
    except Http404:
        if grid == None:
            return ['is new ' + t + ' in grid']
        if designer == None:
            return ['not in designer but is in grid']
    diff = []
    for f in grid._meta.fields:
        if f.name in fks:
            if not f.name.endswith('_ptr'):
                grid_val = getattr(grid, f.name)
                if grid_val:
                    grid_val = grid_val.name
                designer_val = getattr(designer, f.name)
                if designer_val:
                    designer_val = designer_val.name
                if grid_val != designer_val:
                    diff.append(f.name)
        elif f.name != 'id':
            grid_val = getattr(grid, f.name)
            designer_val = getattr(designer, f.name)
            if grid_val != designer_val:
                diff.append(f.name)
    des_loc = DesignerGrid.objects.filter(action=designer)
    grid_loc = Grid.objects.filter(action=grid)
    if len(des_loc) == 1 and len(grid_loc) == 1:
        if des_loc[0].level.slug != grid_loc[0].level.slug:
            diff.append("moved from level %s to %s" % (grid_loc[0].level, des_loc[0].level))
        if des_loc[0].column != grid_loc[0].column:
            diff.append("column changed from %s to %s" % (grid_loc[0].column, des_loc[0].column))
        if des_loc[0].row != grid_loc[0].row:
            diff.append("row changed from %s to %s" % (grid_loc[0].row, des_loc[0].row))
    if len(des_loc) == 1 and len(grid_loc) == 0:
        diff.append("moved to %s from the palette" % des_loc[0].get_loc_str())
    if len(des_loc) == 0 and len(grid_loc) == 1:
        diff.append("moved out of the grid to the palette")
    return diff  # pylint: enable=R0912


def diff_between_designer_and_grid(draft):
    """Returns a list of the action slugs and the changes for those slugs between the
    designer actions and smartgrid actions."""
    ret = []
    for action in DesignerAction.objects.filter(draft=draft):
        slug = action.slug
        diff = diff_between_designer_and_grid_action(draft, slug)
        if len(diff) > 0:
            inner = []
            inner.append(_admin_link(action))
            inner.append(diff)
            ret.append(inner)
    return ret


def load_example_grid(draft, example_name):
    """Loads the Designer with the given example grid. If example_name doesn't exist, nothing
    is changed."""
#     print "load_example_grid(%s, %s)" % (draft, example_name)
#    manage_py = script_utils.manage_py_command()
#    manage_command = "python " + manage_py
    fixture_path = settings.FIXTURE_DIRS[0]

    loaded = False
    # Check to see if there is an example.
    for name in os.listdir(fixture_path):
        if name.startswith(example_name) and name.endswith("_designer.json"):
            # examples exists so clear the designer
            clear_designer(draft)
            # load the example
            fixture = os.path.join(fixture_path, name)
            call_command('loaddata', '-v 0', fixture)
            loaded = True
#            os.system("%s loaddata -v 0 %s" % (manage_command, fixture))
    if loaded:
        # Need to copy everything from None to the draft
        copy_draft(from_draft=None, to_draft=draft)
#     clear_designer(draft=None)
