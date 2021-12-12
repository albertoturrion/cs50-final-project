
// Global variable to control when we should load the test to the user
let first_word = true;

let ids_words = {
    'unlearned': [],
    'learned': [],
    'passed': []
}

// First, we should wait to have the DOM loaded
window.addEventListener('DOMContentLoaded', (event)=> {
    
    // Results page
    let word_data = get_result_saved();
    if (window.location.pathname.includes("/test")) 
    {
        if (first_word = true)
        {
            show_test();
        }
    }

    // Pop-up functionality
    const close_icon = document.querySelector(".popup-wrapper .popup-header span")
    close_icon.addEventListener("click", () => {
        const wrapper = document.querySelector(".popup-wrapper")
        const overlay = document.querySelector(".wrapper-overlay")
        wrapper.remove()
        overlay.remove();
    })

    // Only to notice the user he has finished the test
    // Only display the message if the user comes from /test
    if (document.referrer.includes("/test")){
        // Only display the message if the user is in his list
        if (window.location.pathname.includes("/your-list"))
        {
            const message = "You have finished your test! Check the words in your list."
            show_top_modal(message)
        }
    }

})


// Wait the user click on one bookmark and return the word information
function get_result_saved()
{
    let bookmarks = document.querySelectorAll('.results.material-icons-outlined')
    bookmarks.forEach((bookmark)=>{
        bookmark.addEventListener("click", e => {     
            bookmark_id = e.target.attributes.id.value
            word_bookmarked = get_data_bookmarked(bookmark_id)
            return word_bookmarked;
        });
    });
}

// Taking into account the bookmark clicked, return the word data related to it in a JSON
async function get_data_bookmarked(id)
{
    const user_logged = await get_user_status()
    console.log(user_logged)
    if (user_logged['status'] == null) {
        console.log(user_logged['status']);
        // show pop-up to log-in
        const body = document.querySelector('body')
        const wrapper = document.querySelector(".popup-wrapper");
        const overlay = document.createElement('div')
        overlay.setAttribute('class','wrapper-overlay')
        body.append(overlay)
        wrapper.style['display'] = 'block';


    }
    else {
        word = document.querySelector("#word").textContent
        lexical_category = document.querySelector(`#lexical_category-${CSS.escape(id[0])}`).textContent.replace(/[()]/g,"").toLowerCase()
        definition = document.querySelector(`#definition-${CSS.escape(id)}`).textContent.replace('bookmark_adda','').trim()
        if (definition.slice(0,12) == 'bookmark_add')
        {
            definition = definition.slice(12).trim()
        };
        // It is possible there are more than one example
        examples = []
        examples_clicked = document.querySelectorAll(`#example-${CSS.escape(id)}`)
        examples_clicked.forEach(example => examples.push(example.textContent))
        word_data = {
            'word': word,
            'lexical_category': lexical_category,
            'definition': definition,
            'examples': examples
        }
        const data = await save_word(word_data);
        // if the word has been saved properly, we should notice the user
        if (data.status == 200)
        {
            message = 'The word has been successfully saved!'
            show_top_modal(message)
        }
        console.log(data);
        console.log(data.status);
        
    }
}

async function save_word(word_data)
{
    init = {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(word_data),
        cache: "no-cache",
        headers: {"content-type": "application/json"}
    };

    const response = await fetch(`${window.origin}/save-word`, init);
    if (response.status == 200)
    {
        const data = await response.json()
        return response;
    }
    else
    {
        return 'There was an error saving the word'
    }
}

async function get_words_unlearned()
{
    const response = await fetch("/get-words-unlearned");
    const words = await response.json();
    return words
}

async function show_test() {
    // awaiting for fetching words
    const words = await get_words_unlearned();
    console.log(words)
    console.log("show_words - ids_words", ids_words)
    
    // we only create the ids_unlearned the first time we load the page, after that we'll shift one by one their elements
    if (first_word == true){
        ids_unlearned = Object.keys(words)
        if (ids_unlearned.length === 0 )
        {
            show_top_modal("You don't have any word to learn.")
            return;
        }
        ids_words['unlearned'] = ids_unlearned
    }
    console.log("show_words - ids_words created", ids_words)

    // pick the id of the next word unlearned
    current_id = ids_words['unlearned'][0];
    console.log("Current id:", current_id)

    load_definition(current_id, words)

    let check_button = document.querySelector("#test-check-answer")
    let next_word_button = document.querySelector("#test-next-word")
    let text_correction = document.querySelector("#test-correction")

    // if the user clicks the button "check"
    check_button.addEventListener("click", e => {
        let answer = document.querySelector("#test-answer").value
        correction = check_word(answer, words[ids_words['unlearned'][0]]['word']);
        if (correction == "Correct") {
            // save the id of the definition learned
            if (ids_words['unlearned'].length > 0){
                ids_words['learned'].push(ids_words['unlearned'][0])
            } 
            // remove the id of the learned definition. It returns "undefinied" if there is no more elements
            let definitions_pendant = ids_words['unlearned'].shift()

            // update the value of first_word to avoid loading again all ids_unlearned
            first_word = false;
            text_correction.className = ""
            text_correction.classList.add("answer","correct")
            text_correction.textContent = "Good job!"
            // if there is no more definitions
            if (ids_words['unlearned'].length > 0)
            {
                console.log("Good job! ids_words", ids_words);
                load_definition(ids_words['unlearned'][0], words)
            }
            else
            {
                console.log("Test finished")
                console.log("ids_words", ids_words);
                send_test_result (ids_words)
            }
        }
        else {
            text_correction.className = ""
            text_correction.classList.add("answer","incorrect")
            text_correction.textContent = "Try again!"
        }
    })

    // if the user clicks the button next word
    next_word_button.addEventListener("click", (e)=> {
        // save the id of that word within an array (creating it if not exists)
        ids_words['passed'].push(ids_words['unlearned'][0])
        // first, we should remove that word from ids_unlearned
        ids_words['unlearned'].shift()
        // update the value of first_word to avoid loading again all ids_unlearned
        first_word = false;
        text_correction.className = ""
        text_correction.textContent = ""
        // if it is the last word, finish the test
        if (ids_words['unlearned'].length > 0)
        {
            console.log("Word passed! ids_words", ids_words);
            load_definition(ids_words['unlearned'][0], words)
        }
        // if there is more words, show the next word
        else 
        {
            console.log("Test finished")
            console.log("ids_words", ids_words);
            send_test_result (ids_words)
            window.location.replace("/your-list")
        }
    });
    

}

// we shoud receive the id of the word we should load and the words (definitions) data as a JSON
function load_definition(id, words) {

    // First, we need to store the DOM elements in which we'll add the definition information
    let category = document.querySelector("#test-lexical_category")
    let definition = document.querySelector("#test-definition")
    let div_examples = document.querySelector("#test-examples")

    // if first_word = false (we are loading the rest of the words, then we should clean the examples to avoid repetition)
    // Otherwise, we would be adding each example
    // Same with answer field
    if (first_word == false) {
        existing_examples = document.querySelectorAll(".test_example")
        existing_examples.forEach(e => e.remove())
        // cleaning answer input
        answer = document.querySelector("#test-answer")
        answer.value = "";
    }

    // adding the information to each DOM elements
    category.textContent = words[id]["category"]
    definition.textContent = words[id]["definition"]
    examples = words[id]["example"]
    if (examples[0] != null)
    {
        examples.forEach(example => {
            example_item = document.createElement("li")
            example_item.setAttribute("class", "test_example")
            example_item.innerText = example.replace(words[id]["word"],"_".repeat(words[id]["word"].length))
            div_examples.appendChild(example_item)
        })
    }
}

function check_word(answer, word) {
    let answer_cleaned = answer.toLowerCase().trim();
    console.log(answer_cleaned)
    let word_cleaned = word.toLowerCase().trim();
    console.log(word_cleaned)
    if (word_cleaned === answer_cleaned) {
        return "Correct";
    }
    else {
        return "Try again";
    }
}

function send_test_result (final_result)
{
    fetch ("/save-test-result",
    {
        method: 'POST',
        body: JSON.stringify(final_result),
        headers:{
            'Content-Type': 'application/json'
        }
    }).then(res => res.json())
    .catch(error => console.error('Error:', error))
    .then(response => console.log('Success:', response))
}

async function get_user_status() 
{
    let response = await fetch("/get_user_session")
    res = await response.json()
    console.log(res)
    return res
}

// function to show a modal at the top of the page with a message
function show_top_modal(information)
{
    const modal = document.createElement('div')
    const modal_close = document.createElement('span')
    modal_close.setAttribute('class','material-icons')
    modal_close.textContent = 'close'
    modal.append(modal_close)
    modal.setAttribute('class', 'modal-top')
    const message = document.createElement('p')
    const header = document.querySelector('header')
    message.textContent = information
    modal.append(message)
    header.append(modal)

    // Modal-top close
    // const close_modal = document.querySelector(".modal-top span")
    modal_close.addEventListener("click", () => {
        const modal = document.querySelector('.modal-top')
        modal.remove();
    })
}
