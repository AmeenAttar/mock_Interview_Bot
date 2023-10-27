const ws = new WebSocket('ws://localhost:8000/ws/');

let mediaRecorder;
let stream;
const audioChunks = [];

ws.onopen = function(event) {
    console.log('Connection opened.');
};

// Click event for the "Start Conversation" button
document.getElementById('start').addEventListener('click', function() {
    // Enable the "Mic On" button when "Start Conversation" is clicked
    document.getElementById('micOn').disabled = false;
});

document.getElementById('micOn').addEventListener('click', function() {
    this.disabled = true;
    document.getElementById('micOff').disabled = false;
    startRecording();
});

document.getElementById('micOff').addEventListener('click', function() {
    this.disabled = true;
    document.getElementById('micOn').disabled = false;
    stopRecording();
});

function startRecording() {
    const constraints = { audio: true, video: false };
    navigator.mediaDevices.getUserMedia(constraints).then(function(givenStream) {
        stream = givenStream;
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();

        mediaRecorder.ondataavailable = function(event) {
            audioChunks.push(event.data);
        };
    }).catch(function(err) {
        console.error("Error accessing the microphone:", err);
    });

    mediaRecorder.onstart = function() {
        console.log("Recording started.");
    };
    
    mediaRecorder.ondataavailable = function(event) {
        audioChunks.push(event.data);
        console.log("Audio chunk collected.");
    };
}

function stopRecording() {
    mediaRecorder.stop();
    const audioBlob = new Blob(audioChunks);
    ws.send(audioBlob);
}

ws.onmessage = function(event) {
    const audioBlob = new Blob([event.data], { type: 'audio/mpeg' });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audioElement = new Audio(audioUrl);
    audioElement.play();
}
