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
        }
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
    function highlightError (errorElement, msg)
    {
        msg = msg || "Required";
        errorElement.focus();
        var _popover;
        _popover = errorElement.popover({
            trigger: "manual",
            placement: "top",
            content: msg,
            template: "<div class=\"popover\"><div class=\"arrow\"></div><div class=\"popover-inner\"><div class=\"popover-content\"><p></p></div></div></div>"
        });
        return errorElement.popover("show");
    }
    function validateEmail(email)
    {
        re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email);
    }
    $('#to_payments_button').on('click', function () {
        //e.preventDefault();
        //$('#collapseTwo').collapse('hide');
        $('.popover').hide();
        if ( !$('#firstname').val() )
        {
            highlightError($('#firstname'));
        }
        else if ( !$('#lastname').val() )
        {
            highlightError($('#lastname'));
        }
        else if ( !$('#email').val() )
        {
            highlightError($('#email'));
        }
        else if ( !validateEmail($('#email').val()) )
        {
            highlightError($('#email'), "Invalid email");
        }
        else if ( !$('#address-line1').val() )
        {
            highlightError($('#address-line1'));
        }
        else if ( !$('#address-line2').val() )
        {
            highlightError($('#address-line2'));
        }
        else if ( !$('#address-city').val() )
        {
            highlightError($('#address-city'));
        }
        else if ( !$('#address-state').val() )
        {
            highlightError($('#address-state'));
        }
        else if ( !$('#address-postcode').val() )
        {
            highlightError($('#address-postcode'));
        }
        else
        {
            $('#collapseOne').collapse('hide');
            $('#collapseTwo').collapse('show');
        }
    });
    $('#to_previous_button').on('click', function () {
        //e.preventDefault();
        //$('#collapseTwo').collapse('hide');
        $('#collapseTwo').collapse('hide');
        $('#collapseOne').collapse('show');
    });
    /* $('#collapseOne').on('show', function () {
        $('#collapseTwo').collapse('hide');
    }); */
    /* $('#collapseTwo').on('show', function () {
        $('#collapseOne').collapse('hide');
    }); */
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