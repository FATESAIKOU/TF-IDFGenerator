$(document).ready(function() {
  init();
  event();
});

var database;

function init() {
  $('.resultFile').hide();
  $('.resultString').hide();

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
          produceClassesKeywordTable(database.classes_keyword);
          produceBooksKeywordTable(database.books_keyword, database.books);

          $('.main').hide();
          $('.resultFile').show();
        },
        error: function() {
          Materialize.toast('Upload Error', 4000);
        }
      });
    } else if(type == 'string') {
      data.string = $('#string').val();

      $.post('/php/search.php', data, function(r_string) {
        Materialize.toast(`Submit String Success`, 4000);
        database = JSON.parse(r_string);
        console.log(database);

        if(database.status == 'fail') {
          Materialize.toast('Not Found This Keyword');
          return;
        }

        produceStringBooksKeywordTable(database.tf_idf);

        $('.main').hide();
        $('.resultString').show();
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

function produceClassesKeywordTable(keyword) {
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

  $('#classes_keyword tbody').html(text);
  $('#classes_keyword').DataTable();
}

function produceBooksKeywordTable(keyword, books) {
  var i;
  var text = '';

  var book_id;
  var book_name;
  var word_id;
  var word;
  var value;

  $.each(keyword, function(idx, val) {
    word_id = idx;
    word = val['word'];
    book_id = val['book_id'];
    book_name = books[book_id];
    value = val['value'];

    text += `<tr>`;
    text += `<td>${book_id}</td>`;
    text += `<td>${book_name}</td>`;
    text += `<td>${word_id}</td>`;
    text += `<td>${word}</td>`;
    text += `<td>${value}</td>`;
    text += `</tr>`;
  });

  $('#books_keyword tbody').html(text);
  $('#books_keyword').DataTable();
}

function produceStringBooksKeywordTable(keyword) {
  var i;
  var text = '';

  var book_id;
  var book_name;
  var word_id;
  var word;
  var value;

  $.each(keyword, function(idx, val) {
    book_id = idx;
    word_id = val['word_id'];
    word = val['word_name'];
    book_name = val['book_name'];
    value = val['value'];

    text += `<tr>`;
    text += `<td>${book_id}</td>`;
    text += `<td>${book_name}</td>`;
    text += `<td>${word_id}</td>`;
    text += `<td>${word}</td>`;
    text += `<td>${value}</td>`;
    text += `</tr>`;
  });

  $('#books_string_keyword tbody').html(text);
  $('#books_string_keyword').DataTable();
}

function get_random_color() {
  var letters = 'ABCDE'.split('');
  var color = '#';
  for (var i=0; i<3; i++ ) {
    color += letters[Math.floor(Math.random() * letters.length)];
  }
  return color;
}
