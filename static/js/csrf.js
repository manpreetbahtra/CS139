$(function generate_csrf_token() {
  var alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  var token = '';
  for (var i = 0; i < 32; i++) {
    token += alphabet.charAt(Math.floor(Math.random() * alphabet.length));
  }
  return token;
});
//This function generates a random string of 32 characters that can be used as a CSRF token. 
//Generate a new token every time a form is loaded to help prevent cross-site request forgery attacks- used as a security measure.
