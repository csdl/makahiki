google.load("visualization", "1", {packages:['corechart', 'imagechart']});

// Visualization to show current power data.
function Makahiki_PowerMeter(server_url, wattdepot_version, source, refresh_interval, viz_id, options) {
    // http://code.google.com/apis/visualization/documentation/gallery/genericimagechart.html

    var query = null;
    var source = source;

    // Set a callback to run when the Google Visualization API is loaded.
    google.setOnLoadCallback(callback(source));

    return change_source;

    function getWattdepotGvizURL(source) {
        var gviz_url = null;
        if (wattdepot_version == "WATTDEPOT2") {
    	  // wattdepot2:
           gviz_url = server_url + "/sources/" +
            source + "/gviz/sensordata/latest?tq=select%20timePoint%2C%20powerConsumed";
        }

        if (wattdepot_version == "WATTDEPOT3") {
          // wattdepot3
    	  gviz_url = server_url + "/depository/power/value/gviz/?sensor=" + source + "&latest=true";
        }

        return gviz_url;
    }
    
    function callback(source) {
    	var gviz_url = getWattdepotGvizURL(source);
    	
        query = new google.visualization.Query(gviz_url);
        query.setRefreshInterval(refresh_interval);

        // Set a callback to run when the data has been retrieved.
        query.send(function (response) {
            responseHandler(response);
        });
    }

    function change_source(new_source) {
        source = new_source
        var gviz_url = getWattdepotGvizURL(source);

        query.abort()
        query = new google.visualization.Query(gviz_url);
        query.setRefreshInterval(refresh_interval);
        query.send(function (response) {
            responseHandler(response);
        });
    }

    /** Once data is retrieved, create and display the chart with tooltips. */
    function responseHandler(response) {
        // Process errors, if any.
        if (response.isError()) {
            debug('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
            return;
        }
        // Get the data table.
        var datatable = response.getDataTable();

        // Make the image element.
        draw(datatable);
    }

    // Draws the three components (title, table, caption) of the energy visualization.
    function draw(datatable) {
        // Define look and feel parameters using options object to override defaults.
        var width = options.width || 300;
        var backgroundColor = options.backgroundColor;
        var globalStyle = options.globalStyle || {fontFamily:'sans-serif'};
        var titleStyle = options.titleStyle || {fontWeight:'bold'};
        var captionStyle = options.captionStyle || {fontSize:'0.70em'};
        var powerRange = options.powerRange || 6000;
        var title = options.title;

        // Create a datatable with this source's data and baseline.
        datatable = addBaseline(datatable);

        // Get the top-level div where this visualization should go.
        element = document.getElementById(viz_id);

        // Now add the elements.
        addGlobalStyle(element, backgroundColor, width, globalStyle);
        addTitleDiv(element, viz_id, title, titleStyle);
        addMeterDiv(element, viz_id, datatable, backgroundColor, width, powerRange);
        addCaptionDiv(element, viz_id, captionStyle, datatable);
    }

    // Add baseline value to the power data table
    // Column 0 contains the timestamp.
    // Column 1 contains the power value associated with that timestamp.
    // Column 2 contains baseline value
    function addBaseline(datatable) {
        // Create the data table of power values to return.
        var powerTable = new google.visualization.DataTable();
        var numPowerTableRows = 1;
        powerTable.addColumn('date'); // the time of day.
        powerTable.addColumn('number'); // the power in Wh.
        powerTable.addColumn('number'); // the baseline power in Wh.
        powerTable.addRows(numPowerTableRows);
        var timestampVal = datatable.getValue(0, 0);
        var powerVal = Number(datatable.getValue(0, 1).toFixed(0));
        var baselineVal = 3000;
        powerTable.setCell(0, 0, timestampVal);
        powerTable.setCell(0, 1, powerVal);
        powerTable.setCell(0, 2, baselineVal);
        var dateFormatter = new google.visualization.DateFormat({pattern:'MMM d, yyyy, h:mm:ss a'});
        dateFormatter.format(powerTable, 0);
        return powerTable;
    }

    // Adds 'global' CSS styling to the top-level div passed into this instance.
    function addGlobalStyle(element, backgroundColor, width, globalStyle) {
        if (backgroundColor != null)
            element.style.backgroundColor = backgroundColor;
        element.style.margin = '0 auto';
        element.style.width = width + 'px';
        addStyleProperties(element, globalStyle);
    }

    function addTitleDiv(element, id, title, titleStyle, width) {
        var divId = id + '__Title';
        var div = getElementByIdOrCreate(divId, 'div');
        element.appendChild(div);
        div.style.textAlign = 'center';
        addStyleProperties(div, titleStyle);
        div.style.width = width + 'px';
        if (title)
        	div.innerHTML = title;
    }

    // Updates the divElement style attribute with all properties in styleObject.
    function addStyleProperties(divElement, styleObject) {
        for (key in styleObject) {
            if (styleObject.hasOwnProperty(key)) {
                divElement.style[key] = styleObject[key];
            }
        }
    }

    function addMeterDiv(element, id, datatable, backgroundColor, width, powerRange) {
        var divId = id + '__PowerMeter';
        var div = getElementByIdOrCreate(divId, 'div');

        element.appendChild(div);

        if (backgroundColor != null)
            div.style.backgroundColor = backgroundColor;

        var powerVal = datatable.getValue(0, 1);
        var baselineVal = datatable.getValue(0, 2);
        var minVal = baselineVal - (powerRange / 2);
        var maxVal = baselineVal + (powerRange / 2);

        // Ensure that min value is less than power value by at least 100 W.
        if (powerVal < minVal) {
            minVal = powerVal - 100;
        }
        // Disallow min values less than zero.
        if (minVal < 0) {
            minVal = 0;
        };
        // Make sure that maxVal is greater than powerVal.
        if (powerVal > maxVal) {
            maxVal = powerVal + 300;
        }

        var view = new google.visualization.DataView(datatable);
        view.setColumns([1]);

        var chart = new google.visualization.ImageChart(div);
        chart.draw(view, {cht:'gom',
            chs:width + 'x108',
            chf:'bg,s,' + '00000000', //the last 00 indicates transparency
            chxl:'0:|' + powerVal + ' W|1:|' + minVal + ' W|' + maxVal + ' W',
            chxt:'x,y',
            chco:'3CB371,FFFF00,FF0000',
            chds:minVal + ',' + maxVal,
            chls:'4|12'
        });
    }

    function addCaptionDiv(element, id, captionStyle, datatable) {
        var divId = id + '__Caption';
        var div = getElementByIdOrCreate(divId, 'div');
        div.style.textAlign = 'center';
        element.appendChild(div);
        addStyleProperties(div, captionStyle);
        var lastUpdate = datatable.getFormattedValue(0, 0);
        div.innerHTML = 'As of: ' + lastUpdate;
    }

    // Returns the pre-existing element with id 'id', or else creates and returns
    // a new element with type elementType and that id.
    function getElementByIdOrCreate(id, elementType) {
        var element = document.getElementById(id);
        if (element) {
            return element;
        }
        else {
            element = document.createElement(elementType);
            element.setAttribute("id", id);
            return element;
        }
    }

    /**
     * Outputs the message to the Firebug console window (if console is defined).
     */
    function debug(msg) {
        if (typeof(console) != 'undefined') {
            console.info(msg);
        }
    }
};

