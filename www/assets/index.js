$(document).ready(function() {
  init();
  event();
});

var database;

function init() {
  $('.result').hide();
  $('#type').material_select();// init select
}

function event() {
  $('#type').change(function() {// bind change event
    var type = $(this).val();

    $('.input').hide();
    if(type == 'file') {
      $('#fileWrapper').show();
    } else if(type == 'string') {
      $('#stringWrapper').show();
    }
  })
  .change();// init call function

  $('#submit').click(function() {
    var type = $('#type').val();
    var data = {};
    data.type = type;

    if(type == 'file') {
      // upload file
      $('#fileForm').ajaxSubmit({
        url: '/php/search.php',
        method: 'POST',
        data: data,
        type: 'JSON',
        success: function(r_upload_file) {
          Materialize.toast(`Upload File Success`, 4000);
          database = JSON.parse(r_upload_file);
          console.log(database);

          drawClasses(database.classes_books_num);
          produceKeywordTable(database.classes_keyword);

          $('.main').hide();
          $('.result').show();
        },
        error: function() {
          Materialize.toast('Upload Error', 4000);
        }
      });
    } else if(type == 'string') {
      data.string = $('#string').val();

      $.post('/php/search.php', data, function(result) {
        Materialize.toast(`Submit Success`, 4000);
        console.log(result);
      });
    }
  });
}

function drawClasses(classes) {
  var ctx = $('#classes');
  var options = {
    elements: {
      arc: {
        borderColor: "#000000"
      }
    }
  };
  var data = {
    labels: [],
    datasets: [{
      data: [],
      backgroundColor: [],
      hoverBackgroundColor: []
    }]
  };
  $.each(classes, function(idx, val) {
    var color = get_random_color();
    console.log(idx);
    data.labels.push(`${idx}`);
    data.datasets[0].data.push(val);
    data.datasets[0].backgroundColor.push(color);
    data.datasets[0].hoverBackgroundColor.push(color);
  });

  var myChart = new Chart(ctx, {
    type: 'pie',
    data: data,
    option: options
  });

  console.log('Finish Classes Picture', data);
}

function produceKeywordTable(keyword) {
  var i;
  var text = '';

  var class_id;
  var word_id;
  var word;
  var value;

  $.each(keyword, function(idx, val) {
    word_id = idx;
    word = val['word'];
    class_id = val['class_id'];
    value = val['value'];

    text += `<tr>`;
    text += `<td>${class_id}</td>`;
    text += `<td>${word_id}</td>`;
    text += `<td>${word}</td>`;
    text += `<td>${value}</td>`;
    text += `</tr>`;
  });

  $('#keyword tbody').html(text);
  $('#keyword').DataTable();
}

function get_random_color() {
  var letters = 'ABCDE'.split('');
  var color = '#';
  for (var i=0; i<3; i++ ) {
    color += letters[Math.floor(Math.random() * letters.length)];
  }
  return color;
}
