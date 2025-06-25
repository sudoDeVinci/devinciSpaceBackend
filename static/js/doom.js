"use strict"
const memory = new WebAssembly.Memory({ initial: 108 })

/*stdout and stderr goes here*/
const output = document.getElementById("output")

function readWasmString(offset, length) {
  const bytes = new Uint8Array(memory.buffer, offset, length)
  return new TextDecoder("utf8").decode(bytes)
}

function consoleLogString(offset, length) {
  const string = readWasmString(offset, length)
  console.log('"' + string + '"')
}

function appendOutput(style) {
  return function (offset, length) {}
}

function getMilliseconds() {
  return performance.now()
}

/**@type {HTMLCanvasElement} The "screen" we render to*/
const canvas = document.getElementById("screen")

/**@type {CanvasRenderingContext2D} the context within the canvas so we can manipulate the image buffer more directly*/
const ctx = canvas.getContext("2d", { alpha: false })

const doom_screen_width = 320 * 2
const doom_screen_height = 200 * 2
/**@type {Map<string, number[]>} pixel cache for hex values-memoisation during rendering*/
const colorCache = new Map()

/**@type {ImageData || null} The underlying image Data for our canvas object context.*/
let imageData = null

/**
 * @param {Uint8ClampedArray} data 
 * @param {number} startX 
 * @param {number} startY 
 * @param {number} width 
 * @param {number} blockSize 
 * @param {Uint8ClampedArray} pixelBuffer - Buffer for pixel values, passed by reference and mutated
 */
function getAverageBlockColour(data, startX, startY, width, blockSize, pixelBuffer) {
  let r_sum = 0, g_sum = 0, b_sum = 0
  let i = 0

  for (let y = startY; y < startY + blockSize; y++) {
    for (let x = startX; x < startX + blockSize; x++) {
      i = (y * width + x) * 4;
      r_sum += data[i];
      g_sum += data[i + 1];
      b_sum += data[i + 2];
    }
  }

  // We try this here so we can skip all the pixel calculations
  const key = `${r_sum},${g_sum},${b_sum}${blockSize}`
  /**@type {number[]} */
  let outarr = []

  if (colorCache.has(key)) {
    outarr = colorCache.get(key)
  } else {
    const size = blockSize * blockSize
    outarr[0] = Math.round(r_sum / size)
    outarr[1] = Math.round(g_sum / size)
    outarr[2] = Math.round(b_sum / size)
  }

  pixelBuffer.set(outarr, 0)
  colorCache.set(key, outarr);
}

function drawCanvas(ptr) {
  const doom_screen = new Uint8ClampedArray(
    memory.buffer,
    ptr,
    doom_screen_width * doom_screen_height * 4
  )

  const blockSize = 2
  const scaledWidth = doom_screen_width / blockSize
  const scaledHeight = doom_screen_height / blockSize

  // Set the canvas internal resolution and create ImageData object once.
  if (canvas.width !== scaledWidth || canvas.height !== scaledHeight) {
    canvas.width = scaledWidth
    canvas.height = scaledHeight
    imageData = ctx.createImageData(scaledWidth, scaledHeight)
  }

  const imageDataBuffer = imageData.data
  const pixelBuffer = new Uint8Array(3)

  for (let y = 0; y < scaledHeight; y++) {
    for (let x = 0; x < scaledWidth; x++) {
      getAverageBlockColour(
        doom_screen,
        x * blockSize,
        y * blockSize,
        doom_screen_width,
        blockSize,
        pixelBuffer
      )

      const i = (y * scaledWidth + x) * 4
      imageDataBuffer[i] = pixelBuffer[0]
      imageDataBuffer[i + 1] = pixelBuffer[1]
      imageDataBuffer[i + 2] = pixelBuffer[2]
      imageDataBuffer[i + 3] = 255; // Alpha
    }
  }

  ctx.putImageData(imageData, 0, 0)
}

/*These functions will be available in WebAssembly. We also share the memory to share larger amounts of data with javascript, e.g. strings of the video output.*/
const importObject = {
  js: {
    js_console_log: appendOutput("log"),
    js_stdout: appendOutput("stdout"),
    js_stderr: appendOutput("stderr"),
    js_milliseconds_since_start: getMilliseconds,
    js_draw_screen: drawCanvas,
  },
  env: {
    memory: memory,
  },
}

document.addEventListener("contextmenu", (e) => {
  
    e.preventDefault()

})

WebAssembly.instantiateStreaming(fetch("https://grahamthe.dev/demos/doom/doom.wasm"), importObject).then(
  (obj) => {
    obj.instance.exports.main();

    /*input handling*/
    let doomKeyCode = function (keyCode) {
      // Doom seems to use mostly the same keycodes, except for the following (maybe I'm missing a few.)
      switch (keyCode) {
        case 8:
          return 127 // KEY_BACKSPACE
        case 17:
          return 0x80 + 0x1d // KEY_RCTRL
        case 18:
          return 0x80 + 0x38 // KEY_RALT
        case 37:
          return 0xac // KEY_LEFTARROW
        case 38:
          return 0xad // KEY_UPARROW
        case 39:
          return 0xae // KEY_RIGHTARROW
        case 40:
          return 0xaf // KEY_DOWNARROW
        default:
          if (keyCode >= 65 /*A*/ && keyCode <= 90 /*Z*/) {
            return keyCode + 32 // ASCII to lower case
          }
          if (keyCode >= 112 /*F1*/ && keyCode <= 123 /*F12*/) {
            return keyCode + 75 // KEY_F1
          }
          return keyCode
      }
    }
    let keyDown = function (keyCode) {
      obj.instance.exports.add_browser_event(0 /*KeyDown*/, keyCode)
    }
    let keyUp = function (keyCode) {
      obj.instance.exports.add_browser_event(1 /*KeyUp*/, keyCode)
    }

    /*keyboard input*/
    canvas.addEventListener(
      "keydown",
      function (event) {
        keyDown(doomKeyCode(event.keyCode))
        event.preventDefault()
      },
      false
    )
    canvas.addEventListener(
      "keyup",
      function (event) {
        keyUp(doomKeyCode(event.keyCode))
        event.preventDefault()
      },
      false
    )

    /*mobile touch input*/
    ;[
      ["enterButton", 13],
      ["leftButton", 0xac],
      ["rightButton", 0xae],
      ["upButton", 0xad],
      ["downButton", 0xaf],
      ["ctrlButton", 0x80 + 0x1d],
      ["spaceButton", 32],
      ["altButton", 0x80 + 0x38],
    ].forEach(([elementID, keyCode]) => {
      console.log(elementID + " for " + keyCode)
      var button = document.getElementById(elementID)
      //button.addEventListener("click", () => {keyDown(keyCode); keyUp(keyCode)} );
      button.addEventListener("touchstart", () => keyDown(keyCode))
      button.addEventListener("touchend", () => keyUp(keyCode))
      button.addEventListener("touchcancel", () => keyUp(keyCode))
    })

    /*hint that the canvas should have focus to capute keyboard events*/
    const focushint = document.getElementById("focushint")
    const printFocusInHint = function (e) {
      focushint.innerText =
        "Doom focused, if input stops working focus the game again"
      focushint.style.fontWeight = "normal"
    }
    canvas.addEventListener("focusin", printFocusInHint, false)

    canvas.addEventListener(
      "focusout",
      function (e) {
        focushint.innerText =
          "Click on the Doom game to capute input and start playing."
        focushint.style.fontWeight = "bold"
      },
      false
    )

    canvas.focus()
    printFocusInHint()

    /*Main game loop*/
    function step(timestamp) {
      obj.instance.exports.doom_loop_step()
      window.requestAnimationFrame(step)
    }
    window.requestAnimationFrame(step)
  }
).catch(err => {
  console.error("Failed to load WebAssembly:", err);
})