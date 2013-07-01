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
        $create_form.get(0).submit();
        //console.log(utcDate);
        //picker.setDate(utcDate);

    });
    if (window.location.pathname === "/")
    {
        $('li.active').removeClass();
        $('#campaigns_tab').addClass('active');
    }
    if (window.location.pathname.indexOf("admin") !== -1)
    {
        $('li.active').removeClass();
        $('#admin_tab').addClass('active');
    }
    if (window.location.pathname.indexOf("fundraiser") !== -1 && window.location.pathname.indexOf("admin") === -1)
    {
        $('li.active').removeClass();
        $('#fundraiser_tab').addClass('active');
    }
});