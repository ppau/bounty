$(function() {
    $('#datetimepicker1').datetimepicker({
      pickTime: false
    });
    var $create_form = $('form.create_fundraiser');

    $create_form.submit(function(e) {

        e.preventDefault();
        //var picker = $('#datetimepicker1');
        var picker_date = $('#datetimepicker1').data('datetimepicker').getLocalDate();
        //console.log(picker_date);
        var now = new Date();
        //console.log(now);
        //var outStr = now.getHours()+':'+now.getMinutes()+':'+now.getSeconds();
        var full_date = new Date(picker_date.getFullYear(), picker_date.getMonth(), picker_date.getDate(), now.getHours(), now.getMinutes(), now.getSeconds());
        var utcDate = full_date.toUTCString();
        $('#deadline').val(utcDate);
        //console.log(utcDate);
        //picker.setDate(utcDate);

    });
});