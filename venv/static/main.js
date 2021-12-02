
// First, we should wait to have the DOM loaded
window.addEventListener('DOMContentLoaded', (event)=> {
    
    // Results page
    word_data = get_result_saved()
    get_words_unlearned()


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

function get_words_unlearned()
{
    fetch("/get-words-unlearned")
    .then(response => {
        return response.json()
    })
    .then(text => {
        console.log(text)
    })

}