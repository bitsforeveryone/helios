var currentChallenge = ""
$('#challengeAttemptModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    currentChallenge = button.data('chalname') // Extract info from data-* attributes
    var challengePrototype = button.data('chalprototype')
    var challengeDesc = button.data('chaldesc')
    var modal = $(this)
    modal.find('#challengeAttemptTitle').text('Attempting: ' + currentChallenge)
    modal.find('#codeSubmitTextArea').val(challengePrototype)
    modal.find("#challengeInfo").text(challengeDesc)
    resetAlerts();
})
$('#submitattempt').click(function () {
    resetAlerts();
    var userSubmission = $("#codeSubmitTextArea").val()
    $('#gradingLoaderCtr').removeClass("d-none")
    $.post("/artemis/submit",
        {
            challenge: currentChallenge,
            submission: userSubmission
        },
        function (data) { //success callback
            receiveResults(data)
        }).fail(function (response) {
        receiveResults("error")
    });
});

// based on results data passed back, show success or failure alert
function receiveResults(data) {

    if (data["result"] === "Success") {
        $('#gradingResultAlertSuccess').removeClass("d-none");
        $('#gradingResultAlertSuccess').html("<strong>Good job!</strong> That checks out.")
    } else {
        $('#gradingResultAlertFailure').removeClass("d-none");
        if (data["result"]==="Failure") {
            $('#gradingResultAlertFailure').html("<strong>Oops, that's not it</strong>" +
                "<hr>" +
                "<p>Expected: </p><pre><div class='codeSample'>"+data["response"]["expected"]+"\n</div></pre></p>"+
                "<p>Received: </p><pre><div class='codeSample'>"+data["response"]["received"]+"\n</div></pre></p>")
        }
        else if (data["result"]==="Error") {
            $('#gradingResultAlertFailure').html("<strong>Program failed to start</strong>" +
                "<hr>"+
                data["response"]["received"])
        }
    }
    $('#gradingLoaderCtr').addClass("d-none")
}

function resetAlerts() {
    $('#gradingResultAlertSuccess').addClass("d-none");
    $('#gradingResultAlertSuccess').html()
    $('#gradingResultAlertFailure').addClass("d-none");
    $('#gradingResultAlertFailure').html()
}