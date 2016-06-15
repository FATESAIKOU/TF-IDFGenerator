$(document).ready(function() {
  $('#type').material_select();// init select
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
      console.log(data);

      $('#fileForm').ajaxSubmit({
        url: 'search.php',
        method: 'POST',
        data: data,
        type: 'JSON',
        success: function(result) {
          console.log(result);
        }
      });
    } else if(type == 'string') {
      data.string = $('#string').val();

      console.log(data);
      $.post('search.php', data, function(result) {
        console.log(result);
      });
    }
  });
});

