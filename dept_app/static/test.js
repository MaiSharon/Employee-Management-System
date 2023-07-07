$(document).ready(function(){
    var board = $('#board');
    var columns = ['To Do', 'In Progress', 'Done'];
    for (var i = 0; i < columns.length; i++) {
        var column = $('<div>').addClass('card').css('width', '18rem').appendTo(board);
        $('<div>').addClass('card-header').text(columns[i]).appendTo(column);
        var listGroup = $('<ul>').addClass('list-group list-group-flush').appendTo(column);
        for (var j = 0; j < 9; j++) {
            $('<li>').addClass('list-group-item').text(columns[i] + ' Item ' + (j + 1)).appendTo(listGroup);
        }
    }
});
