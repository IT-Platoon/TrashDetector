"use strict";

const video = document.getElementById('video');

// peer connection
let pc = null;

// data channel
let dc = null, dcInterval = null;


const srcVideo = document.getElementById('srcVideo');
const videoInput = document.getElementById('videoFile');
videoInput.addEventListener("change", function() {
  srcVideo.src = URL.createObjectURL(this.files[0]);
});

const select = document.getElementById('select');
let selectValue = select.value;
select.addEventListener('change', () => {
  selectValue = select.value;

  if (selectValue === 'video') {
    videoInput.classList.remove('disabled');
  } else {
    videoInput.classList.add('disabled');
  }

});


function createPeerConnection() {
  const config = {
    sdpSemantics: 'unified-plan'
  };

  if (false) {
    config.iceServers = [{urls: ['stun:stun.l.google.com:19302']}];
  }

  pc = new RTCPeerConnection(config);

  // connect audio / video
  pc.addEventListener('track', function(evt) {
    if (evt.track.kind === 'video') {
      video.srcObject = evt.streams[0];
      video.playbackRate = 4.0;
    } else {
      document.getElementById('audio').srcObject = evt.streams[0];
    }
  });

  return pc;
}

function negotiate() {
  return pc.createOffer()
    .then((offer) => pc.setLocalDescription(offer))
    .then(() => new Promise((resolve) => {
        if (pc.iceGatheringState === 'complete') {
          resolve();
        } else {
          function checkState() {
            if (pc.iceGatheringState === 'complete') {
              pc.removeEventListener('icegatheringstatechange', checkState);
              resolve();
            }
          }
          pc.addEventListener('icegatheringstatechange', checkState);
        }
      })
    )
    .then(() => {
      const offer = pc.localDescription;

      return fetch('/cv', {
        body: JSON.stringify({
          sdp: offer.sdp,
          type: offer.type,
        }),
        headers: {
          'Content-Type': 'application/json'
        },
        method: 'POST'
      });
    })
    .then((response) => response.json())
    .then((answer) => pc.setRemoteDescription(answer))
    .catch(alert);
}

function start() {
  pc = createPeerConnection();

  let time_start = null;

  function current_stamp() {
    if (time_start === null) {
      time_start = new Date().getTime();
      return 0;
    } else {
      return new Date().getTime() - time_start;
    }
  }

  const parameters = {"ordered": false};

  const constraints = {video: true};

  function addStream(stream) {
    stream.getTracks().forEach((track) => {
      if (track.kind === 'video') {
        const {width, height} = track.getSettings();
        video.setAttribute('width', width.toString());
        video.setAttribute('height', height.toString());

        track.applyConstraints({ frameRate: { ideal:5, max: 10 } });
      }

      pc.addTrack(track, stream);
    });
    return negotiate();
  }

  if (selectValue === 'video') {
    addStream(srcVideo.captureStream());
    srcVideo.currentTime = 0;
    srcVideo.play();
  } else if (constraints.audio || constraints.video) {
    navigator.mediaDevices.getUserMedia(constraints)
      .then(addStream)
      .catch((err) => alert('Could not acquire media: ' + err));
  } else {
    negotiate();
  }
}

function stop() {
  srcVideo.pause();

  // close transceivers
  if (pc.getTransceivers) {
    pc.getTransceivers().forEach(function(transceiver) {
      if (transceiver.stop) {
        transceiver.stop();
      }
    });
  }

  // close local audio / video
  pc.getSenders().forEach(function(sender) {
    sender.track.stop();
  });

  // close peer connection
  setTimeout(function() {
    pc.close();
  }, 500);
}

let isStart = false;
const toggleButton = document.getElementById('toggle');
toggleButton.addEventListener('click', () =>  {
  isStart = !isStart;
  if (isStart) {
    toggleButton.innerText = 'Остановить';
    start();
  } else {
    toggleButton.innerText = 'Запустить';
    stop();
  }
});
