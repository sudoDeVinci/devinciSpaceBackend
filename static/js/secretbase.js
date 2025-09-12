
/**
 * 
 * @param {HTMLButtonElement} button 
 * @param {HTMLInputElement} textInput 
 * @param {string} endpoint 
 */
function assignButtonInputToEndpoint(button, textInput, endpoint) {
    button.onclick = e => {
            console.log(textInput.value)
            fetch(endpoint, {
                method: 'GET'
            }).then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error('Error:', error))
        }
}

const button = document.getElementById('secret-submit-btn')
const textInput = document.getElementById('secretinput')
const endpoint = `/secretcheck?secret="${textInput.value}"`

console.log(button, textInput, endpoint)

assignButtonInputToEndpoint(button, textInput, endpoint)
