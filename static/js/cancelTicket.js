console.log("cancelTicket.js loaded");
$(document).ready(function() {
    $("#cancelTicket").click(function(event) {
      event.preventDefault();
      var confirmed = confirm("Are you sure you want to cancel?");
      if (confirmed) {
        $(this).closest("form").submit();
      }
    });
  });

  // the cancel ticket button has an id cancel ticket which is used here. If the buttin is clicked, confirmation is asked, so that they dont accidentally cancel tickets. 
