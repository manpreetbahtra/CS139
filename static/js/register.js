// get the registration form element
//I gave the registration form an id (registration-form) that I am able to use here. 
const registrationForm = document.getElementById('registration-form');

$( function() {
  alert("Welcome to the Giginator");
});

// getting the registration form using a combination of css and the factory method
$('#registration-form').submit(function() {
  var username = document.registration.username.value;
  var email = document.registration.email.value;
  var user_type = document.registration.user-type.value;
  var registrationCode=document.registration.registration-code.value; 
  var password = document.registration.password.value;
  var confirm_password = document.registration.confirm_password.value;

  if (passwordValidation(password,8,13) && allLetter(username) &&validateEmail(email) && passwordMatch(password, confirm_password) &&organiserCode(user_type, registrationCode) ){
    alert('Registration successful');
    return true;
  }
  alert('Registration not successful ');
  return false;

});

// form validation functions
function passwordValidation(password,min,max){
  var passwordLength = password.value.length;
  if (passwordLength == 0 || passwordLength >= max || passwordLength < min){
    alert("Password should not be empty / length be between "+min+" to "+max);
    password.focus();
    return false;
  } 
  return true;
}

function allLetter(username){ 
  var letters = /^[A-Za-z]+$/;
  if(username.value.match(letters)){
    return true;
  }else{
    alert('Username must have alphabet characters only');
    username.focus();
    return false;
  }
}

function validateEmail(email){
  var mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
  if(email.value.match(mailformat)) {
    return true;
  } else{
    alert("You have entered an invalid email address!");
    email.focus();
    return false;
  }
}

function passwordMatch(password, confirm_password){
  if(password != confirm_password ){
    alert("Password does not match confirmation");
    return false;
  }
  return true;
}

function organiserCode(user_type, registrationCode){
  if (user_type === 'organiser' && registrationCode !== 'Dc5_G1gz') {
    alert('Invalid registration code.');
    return false ;
  }
  else {
    return true; 
  }
}

