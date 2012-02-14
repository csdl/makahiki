// Load the Visualization API and the bar chart package.
google.load("visualization", "1");

function initializeMonitor(charturl, dorm, team) {
  var powerLastCheck = document.getElementById('powerlastcheck');
  var energyLastCheck = document.getElementById('energylastcheck');
  
  powerLastCheck.innerHTML = generateCheckDate();
  energyLastCheck.innerHTML = generateCheckDate();
  
  // Get all of the dorm data from the spreadsheet.
  var dormDataURL = charturl;
  var dorm = dorm;
  var team = team;
  var dormDataQuery = new google.visualization.Query(dormDataURL);
  // Update the chart every 30 seconds
  dormDataQuery.setRefreshInterval(30);
  // Set a callback to run when the dorm data has been retrieved.
  dormDataQuery.send(displayDormData);
}


/**
 * Once data is available, create view to display.
 */
function displayDormData(response) {
  // Process errors, if any.
  if (response.isError()) {
      alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
      return;
  }
  
  // Get the dorm data table.
  var data = response.getDataTable();
  
  var view = new google.visualization.DataView(data);
  //Find the row corresponding to the dorm and team.  Dorm is column 0, Team is column 1.
  //Should we do anything if there is more than one row?
  view.setRows(view.getFilteredRows([{column: 0, value: dorm}, {column: 1, value: team}]));
  
  //Create power monitor.  Column 2 is the power value, column 3 is the update date.
  drawMonitor(document.getElementById("powerdata"), "Watts", view, 2, 3);
  
  //Create energy monitor. Column 4 is the value, column 5 is the update date.
  drawMonitor(document.getElementById("energydata"), "Watt Hours", view, 4, 5);             
}

function generateCheckDate() {
  var html = [];
  var checkDate = new Date();
  var months = new Array('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec');
  html.push("<font style = \"font-size:0.8em; font-style: italic\">Last check was at: ");
  html.push(months[checkDate.getMonth()]);
  html.push(" " + checkDate.getDate() + ", " + checkDate.getFullYear() + " ");
  html.push(checkDate.toLocaleTimeString());
  html.push("</font>");
  return html.join('');
}

function drawMonitor(datadiv, unit, data, valueIndex, dateIndex) {
  var html = [];
  var date = data.getFormattedValue(0, dateIndex)
  var value = data.getFormattedValue(0, valueIndex)
  value = parseFloat(value);
  value = Math.team(value + 0.5);
  html.push('<font style=\"font-size:1.2em; font-weight:bold; font-family:arial,sans-serif\">');
  html.push(value);
  html.push('</font>');
  html.push(' ');
  html.push(unit);
  html.push('<br /><font style=\"font-size:0.8em; font-style: italic\">Data Updated at: '); 
  html.push(date);
  html.push('</font>');
  
  datadiv.innerHTML = html.join('');
}

