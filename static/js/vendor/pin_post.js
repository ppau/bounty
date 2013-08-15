$(function() {

  // Firstly, set the publishable key
  //
  // This can either be your live publishable key or test publishable key, depending
  // on which script you included above

  Pin.setPublishableKey(pin_public_key);

  // Now we can call Pin.js on form submission to retrieve a card token and submit
  // it to the server

  var $form = $('form.pin'),
      $submitButton = $form.find(":submit"),
      $errors = $('.pin-errors');

  $form.submit(function(e) {

    e.preventDefault();
    $errors.hide();

    // Fetch details required for the createToken call to Pin
    var card = {
      number: $('#cc-number').val(),
      name: $('#cc-name').val(),
      expiry_month: $('#cc-expiry-month').val(),
      expiry_year: $('#cc-expiry-year').val(),
      cvc: $('#cc-cvc').val(),
      address_line1: $('#address-line1').val(),
      address_line2: $('#address-line2').val(),
      address_city: $('#address-city').val(),
      address_state: $('#address-state').val(),
      address_postcode: $('#address-postcode').val(),
      address_country: $('#address-country').val()
    };

    var hasError = false;

    if ($("#amount").val() === "" || $("#amount").val() === null ||
          parseFloat($("#amount").val()) < 5 ) {
        hasError = true;
        $("#amount").closest(".control-group").addClass("error");
    }
    else if ($("#amount").closest(".control-group").hasClass("error") &&
      parseFloat($("#amount").val()) >= 5) {
      $("#amount").closest(".control-group").removeClass("error");
    hasError = false;
    }

    if (hasError === false) {
     // Disable the submit button to prevent multiple clicks
      $submitButton.attr({disabled: true});
      $submitButton.val("Processing donation...");
      $("#loading").modal('show');
      // Request a token for the card from Pin
      Pin.createToken(card, handlePinResponse);
    }
    else {
      $(".error").first().find("input, select").focus();
    }

  });

  function handlePinResponse(response) {
    var $form = $('form.pin');

    if (response.response) {
      // Add the card token and ip address of the customer to the form
      // You will need to post these to Pin when creating the charge.
      $('<input>')
        .attr({type: 'hidden', name: 'card_token'})
        .val(response.response.token)
        .appendTo($form);
      $('<input>')
        .attr({type: 'hidden', name: 'ip_address'})
        .val(response.ip_address)
        .appendTo($form);

      // Resubmit the form
      $form.get(0).submit();

    } else {
      var $errorList = $errors.find('ul');

      $errors.find('h4').text(response.error_description);
      $errorList.empty();

      $.each(response.messages, function(index, errorMessage) {
        if(errorMessage.param == 'number') {
            $('#cc-number-error').text(errorMessage.message);
            $('#cc-number-error').show();
            $('#cc-number-error').parents(".control-group").addClass('error');
        }
        else if (errorMessage.param == 'name') {
            $('#cc-name-error').text(errorMessage.message);
            $('#cc-name-error').show();
            $('#cc-name-error').parents(".control-group").addClass('error');
        }
        else if (errorMessage.param == 'expiry_year') {
            $('#cc-year-error').text(errorMessage.message);
            $('#cc-year-error').show();
            $('#cc-year-error').parents(".control-group").addClass('error');
        }
        else if (errorMessage.param == 'expiry_month') {
            $('#cc-month-error').text(errorMessage.message);
            $('#cc-month-error').show();
            $('#cc-month-error').parents(".control-group").addClass('error');
        }
        else
            $('<li>').text(errorMessage.param + ": " + errorMessage.message).appendTo($errorList);
      });

      $errors.show();
      $submitButton.removeAttr('disabled');
      $submitButton.val("Donate now");
      $("#loading").modal('hide');
    }
  }
});