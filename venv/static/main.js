
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
    if (first_word = true)
    {
        show_test()
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
function get_data_bookmarked(id)
{
    word = document.querySelector("#word").textContent
    lexical_category = document.querySelector(`#lexical_category-${CSS.escape(id[0])}`).textContent.replace(/[()]/g,"").toLowerCase()
    definition = document.querySelector(`#definition-${CSS.escape(id)}`).textContent.replace('bookmark_adda','').trim()
    if (definition.slice(0,12) == 'bookmark_add'){
        definition = definition.slice(12).trim()
    }
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
    save_word(word_data)
}

function save_word(word_data)
{
    init = {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(word_data),
        cache: "no-cache",
        headers: {"content-type": "application/json"}
    };

    fetch(`${window.origin}/save-word`, init)
        .then((response) => {
            if(response.status !== 200)
            {
                console.log(`There was a problem saving the word. Status code: ${response.status}`);
                return;
            }
            response.json().then(data=> console.log(data));
        })
        .catch(error => console.log(`Fetch error: ${error}`))
}

async function get_words_unlearned()
{
    const response = await fetch("/get-words-unlearned");
    const words = await response.json();
    return words
}

async function show_test() {
    const words = await get_words_unlearned();
    console.log(words)
    console.log("show_words - ids_words", ids_words)
    
    // we only create the ids_unlearned the first time we load the page, after that we'll shift one by one their elements
    if (first_word == true){
        ids_unlearned = Object.keys(words)
        ids_words['unlearned'] = ids_unlearned
    }
    console.log("show_words - ids_words created", ids_words)
    

    console.log("ids_unlearned:", ids_unlearned)

    // pick the id of the next word unlearned
    current_id = ids_words['unlearned'][0];
    console.log("Current id:", current_id)

    // getting the first word
    let word = words[current_id]["word"]
    console.log(word)

    let category = document.querySelector("#test-lexical_category")
    let definition = document.querySelector("#test-definition")
    let div_examples = document.querySelector("#test-examples")
    let check_button = document.querySelector("#test-check-answer")
    let next_word_button = document.querySelector("#test-next-word")
    let text_correction = document.querySelector("#test-correction")

    load_definition(current_id, category, definition, div_examples, words)

    // if the user clicks the button "check"
    check_button.addEventListener("click", e => {
        let answer = document.querySelector("#test-answer").value
        correction = check_word(answer, word);
        if (correction == "Correct") {
            // remove the id of the learned definition. It returns "undefinied" if there is no more elements
            let definitions_pendant = ids_words['unlearned'].shift()

            // save the id of the definition learned
            if (definitions_pendant != undefined){
                ids_words['learned'].push(current_id)
            } 
            // update the value of first_word to avoid loading again all ids_unlearned
            first_word = false;
            text_correction.className = ""
            text_correction.classList.add("answer","correct")
            text_correction.textContent = "Good job!"
            // if there is no more definitions
            if (ids_words['unlearned'].length > 0)
            {
                console.log("Good job! ids_words", ids_words);
                show_test()
            }
            else
            {
                console.log("Finished! ids_words", ids_words);
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
        ids_words['passed'].push(current_id)
        // first, we should remove that word from ids_unlearned
        ids_words['unlearned'].shift()
        // update the value of first_word to avoid loading again all ids_unlearned
        first_word = false;
        text_correction.className = ""
        // if it is the last word, finish the test
        if (ids_words['unlearned'].length > 0)
        {
            console.log("Word passed! ids_words", ids_words);
            e.stopImmediatePropagation()
            show_test()
            console.log("Click event loop finished");
        }
        // if there is more words, show the next word
        else 
        {
            console.log("Test finished")
            console.log("ids_words", ids_words);
        }
    });
    

}

function load_definition(id, category, definition, div_examples, words) {
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
    category.textContent = words[id]["category"]
    definition.textContent = words[id]["definition"]
    examples = words[id]["example"]
    examples.forEach(example => {
        example_item = document.createElement("li")
        example_item.setAttribute("class", "test_example")
        example_item.innerText = example.replace(words[id]["word"],"_".repeat(words[id]["word"].length))
        div_examples.appendChild(example_item)
    })
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

