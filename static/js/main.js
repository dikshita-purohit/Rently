function validateForm(){
    var username = document.getElementById('name').value;
    var email_id = document.getElementById('email').value;
    var password = document.getElementById('pass').value;
    var re_password = document.getElementById('re_pass').value;

    if( username === "" || email_id === "" || password === "" || re_password === ""){
        alert("Plese fill all the Details.");
        return false;
    }
    else{
       alert("Sign-up Successfull");
       return true;
    }
   }