// Visualization to show current power data.
Makahiki_PowerMeterStatus = function (server_url, wattdepot_version, source, refresh_interval, viz_name, options, id) {
    var testDate = new Date();
    var catLength = testDate.toString().indexOf("GMT");
    var yearLoc = testDate.toString().indexOf(testDate.getFullYear()) + 4;
    return callback();

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

    function callback() {
        var gviz_url = getWattdepotGvizURL(source);

        var query = new google.visualization.Query(gviz_url);
        query.setRefreshInterval(refresh_interval);

        // Set a callback to run when the data has been retrieved.
        query.send(function (response) {
            responseHandler(response, viz_name + ""+ id, refresh_interval, id);
        });
    }

    /** Once dorm data is retrieved, create and display the chart with tooltips. */
    function responseHandler(response, viz_name, rf_interval, id) {
        // Process errors, if any.
        if (response.isError()) {
            debug('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
            return;
        }
        // Get the dorm data table.
        var datatable = response.getDataTable();

        // Get timestamp
        datatable = addBaseline(datatable);
        var lastUpdate = datatable.getFormattedValue(0, 0);
        var now = new Date();
        var then = new Date(lastUpdate);
        var diff = now.getTime() - then.getTime();
        then = then.toString();
        
        $("#last-check").html("Last Check: " + now.toLocaleTimeString());
        $("#"+ viz_name).html(format_num( Math.round(diff / 1000)) + " s  ");
        if (diff / 1000 > 2 * rf_interval) {
            $("#"+ viz_name).html("Last Reported: " + lastUpdate + "&nbsp;&nbsp;&nbsp;&nbsp;" + format_num( Math.round(diff / 1000)) + " s  ");
            $("#" + viz_name).css('color', 'red');
            $("#" + viz_name).css('font-face', 'bold');
       }
       else {
          $("#"+ viz_name).css('color', 'black');
      } 
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

  function format_num(num) {
       return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

};

