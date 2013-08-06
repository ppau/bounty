$(function() {
    $('#datetimepicker1').datetimepicker({
      pickTime: false
    });
    // for some reason without this setLocalDate defaults to today when you call it later on...
    var $date_picker = $('#datetimepicker1').data('datetimepicker');
    if ($date_picker)
    {
        $date_picker.setLocalDate(null);
    }
    var $create_form = $('form.create_fundraiser');

    $create_form.submit(function(e) {

        e.preventDefault();
        var picker_date = $('#datetimepicker1').data('datetimepicker').getLocalDate();
        if (picker_date)
        {
            var now = new Date();
            var full_date = new Date(picker_date.getFullYear(), picker_date.getMonth(), picker_date.getDate(), now.getHours(), now.getMinutes(), now.getSeconds());
            var utcDate = full_date.toUTCString();
            $('#deadline').val(utcDate);
        };
        $create_form.get(0).submit();
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
    if ($("#cc-expiry-year").length){
        var thisYear = new Date().getFullYear(),
        year_node = $("#cc-expiry-year");
        for (var i = thisYear; i < thisYear + 12; ++i) {
            $(document.createElement('option')).attr('value', i).text(i)
                .appendTo(year_node);
        }
    }
    $('#collapseTwo').on('show', function () {
        $('#collapseOne').collapse('hide');
    });
    $('#collapseOne').on('show', function () {
        $('#collapseTwo').collapse('hide');
    });
    $('#load_fundraisers').on("click", function(){
        $('#campaign_container').load('/a/fundraiser');
        $('.btn.active').removeClass('active');
        $('#load_fundraisers').addClass('active');
    });
    $('#load_petitions').on("click", function(){
        $('#campaign_container').load('/a/petition');
        $('.btn.active').removeClass('active');
        $('#load_petitions').addClass('active');
    });
    $('#load_group').on("click", function(){
        $('#campaign_container').load('/a/group_purchase');
        $('.btn.active').removeClass('active');
        $('#load_group').addClass('active');
    });
    $('#load_all').on("click", function(){
        $('#campaign_container').load('/a/all');
        $('.btn.active').removeClass('active');
        $('#load_all').addClass('active');
    });
    $('#citizen-status').change(function() {

        if ($('form input[type=radio]:checked').val() === 'no')
        {
            $('#citizen-error').show();
            $('#to_payments_button').hide();
        }
        else if ($('#citizen-error').is(":visible") && $('form input[type=radio]:checked').val() === 'yes')
        {
            $('#citizen-error').hide();
            $('#to_payments_button').show();
        }
    });
});