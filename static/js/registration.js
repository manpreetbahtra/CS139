$( function() {
    alert("Hello from javascript");
});

$('#form').submit(function() {
    var fullname = document.registration.fullname;
    var email = document.registration.email;
    var username = document.registration.username;
    var password = document.registration.password;

    if (passwordValidation(password,min,max) && allLetter(username) &&validateEmail(email) ){
        alert('Form submitted');
        return true;
    }
    alert('not submitted ');
    return false;

});

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
    }
    else{
        alert('Username must have alphabet characters only');
        username.focus();
        return false;
    }
}

function validateEmail(email){
var mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
if(email.value.match(mailformat))
{
return true;
}
else
{
alert("You have entered an invalid email address!");
email.focus();
return false;
}
}
