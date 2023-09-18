


  $(function() {
    $(".complete-btn").click(function(event) {
      id = this.id;
      console.log(id);
      alert("DONE");
      $('td').css('background-color', 'green', 'line-through');
      $('#' + id).closest('td').prev().css('text-decoration', 'line-through');
      console.log("done");
    })
  });

  // var xmlhttp = new XMLHttpRequest();
  // xmlhttp.open("POST", "newList");
  // xmlhttp.send(); // For POST requests

  // xmlhttp.onreadystatechange=function() {
  // if (xmlhttp.readyState==4 && xmlhttp.status==200){
  //   document.getElementById("id").innerHTML=xmlhttp.responseText;
  // }
// }

