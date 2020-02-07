// The max and min number of photos a customer can purchase


/* Handle any errors returns from Checkout  */
var handleResult = function (result) {
    if (result.error) {
        var displayError = document.getElementById("error-message");
        displayError.textContent = result.error.message;
    }
};

// Create a Checkout Session with the selected quantity
var createCheckoutSession = function () {
    var formData = new FormData(document.querySelector('#form1'))
    console.log(formData.get('user_name'))
    return fetch("/create-checkout-session", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            quantity: 1,
            patient: formData.get('user_name'),
            medication: formData.get('user_medication'),
            pharmacy: formData.get('user_pharmacy'),
            locale: i18next.language.toLowerCase(),
        })
    }).then(function (result) {
        return result.json();
    });
};

var run;
/* Get your Stripe publishable key to initialize Stripe.js */
fetch("/config")
    .then(function (result) {
        return result.json();
    })
    .then(function (json) {
        window.config = json;
        var stripe = Stripe(config.publicKey);
        // Setup event handler to create a Checkout Session on submit

        document.querySelector('#form1').addEventListener('submit', function (evt) {
            evt.preventDefault();
            createCheckoutSession().then(function (data) {
                stripe
                    .redirectToCheckout({
                        sessionId: data.sessionId
                    })
                    .then(handleResult);
            });

        })


    });


/*BUTTONS*/

let vis = false
let showScript = function () {
    // document.getElementById('script').style.display = "block"
    if (!vis) {
        $('#script').show();
        $('#script').removeClass('out').addClass('active');

    } else {
        $('#script').removeClass('active').addClass('out');

        setTimeout(function () {
            $('#script').hide()
        }, 300); //Same time as animation
    }
    vis = !vis;
}

// $('#script').on('click', function (e) {
//     $('#script').show();
//     $('#script').removeClass('out').addClass('active');
// });

// $('#script').on('click', function (e) {
//     $(this).removeClass('active').addClass('out');
//
//     setTimeout(function () {
//         $('#script').hide()
//     }, 300); //Same time as animation
// });