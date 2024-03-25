window.onpopstate = function (event) {
    if (event.state) {
        console.log(event.state.results);
        post_results(event.state.results);
    }
}


function convertToInternationalCurrencySystem(number) {
    if (number === undefined) {
        return "N/A";
    } else {
        number = number.replace(",", "");

        // Remove results that are not very popular
        if (number < 100) {
            return "remove";
        }

        // Nine Zeroes for Billions
        return Math.abs(Number(number)) >= 1.0e+9

            ?
            (Math.abs(Number(number)) / 1.0e+9).toFixed(2) + "B"
            // Six Zeroes for Millions
            :
            Math.abs(Number(number)) >= 1.0e+6

            ?
            (Math.abs(Number(number)) / 1.0e+6).toFixed(2) + "M"
            // Three Zeroes for Thousands
            :
            Math.abs(Number(number)) >= 1.0e+3

            ?
            (Math.abs(Number(number)) / 1.0e+3).toFixed(2) + "K"

            :
            Math.abs(Number(number));
    }
}

function reset() {
    // Reset placeholder value
    let input = document.querySelector("#title");
    input.placeholder = "Type to search";
    document.querySelector("#loading").style.display = "none";
}


document.addEventListener("DOMContentLoaded", function () {


    let submit = document.querySelector("#submit");
    let search = document.querySelector("#search");

    if (document.querySelectorAll('button[name="preclick"]') != null) {
        const buttons = document.querySelectorAll('button[name="preclick"]');
        buttons.forEach(button => {
            button.onclick = () => {
                const imdb_id = button.dataset.id;
                const span = document.getElementById(`${imdb_id}`);
                const value = document.getElementById(`${imdb_id}Value`).dataset.rating;
                span.querySelector(`.star-${value}`).click();
            }
        })
    }


    if (document.querySelectorAll('button[name="toggle"]') != null) {
        const buttons = document.querySelectorAll('button[name="toggle"]');
        var count = document.querySelector('#count');
        buttons.forEach(button => {
            button.onclick = function () {
                const imdb_id = this.dataset.id;
                if (this.innerHTML === "+ Add to Watchlist") {
                    // Get card id, title, description, image, rating, and votes
                    const title = this.dataset.title;
                    const description = this.dataset.description;
                    const image = this.dataset.image;
                    const imdbRating = this.dataset.rating;
                    const imdbVotes = this.dataset.votes;

                    // Post results
                    fetch('/add', {
                            method: 'POST',
                            body: JSON.stringify({
                                imdb_id: imdb_id,
                                title: title,
                                description: description,
                                image: image,
                                imdbRating: imdbRating,
                                imdbVotes: imdbVotes
                            })
                        })
                        .then(response => {
                            console.log(response.json());
                            if (response.status === 201) {
                                // Change button text
                                this.className = "btn btn-outline-secondary";
                                this.innerHTML = "✓ In Watchlist";
                                count.textContent = String(Number(count.textContent) + 1);
                            }
                        })
                        .catch(error => {
                            reset()
                            console.log(error);
                        });
                } else if (this.innerHTML === "✓ In Watchlist") {
                    // Post results
                    fetch('/remove', {
                            method: 'POST',
                            body: JSON.stringify({
                                imdb_id: imdb_id
                            })
                        })
                        .then(response => {
                            console.log(response.json());
                            if (response.status === 201) {
                                // Change button text
                                this.className = "btn btn-outline-warning";
                                this.innerHTML = "+ Add to Watchlist";
                                let val = Number(count.textContent) - 1;
                                if (val != 0) {
                                    count.textContent = String(val);
                                } else {
                                    count.textContent = "";
                                }
                            }
                        })
                        .catch(error => {
                            reset()
                            console.log(error);
                        });
                }
            };
        });
    }

    submit.addEventListener("click", (event) => find(event));
    search.addEventListener("submit", (event) => find(event));

    $('.stars a').on('click', function (event) {
        event.preventDefault();
        $('.stars span, .stars a').removeClass('active');
        $(this).addClass('active');
        $('.stars span').addClass('active');
        var rating = this.innerHTML;
        const imdb_id = this.parentElement.id;
        const button = document.querySelector(`#Rate${imdb_id}`);
        let review = document.querySelector(`#Review${imdb_id}`);
        button.disabled = false;
        button.onclick = function () {
            const title = this.dataset.title;
            const description = this.dataset.description;
            const image = this.dataset.image;
            const imdbRating = this.dataset.rating;
            const imdbVotes = this.dataset.votes;
            // Post rating
            fetch('/rating', {
                    method: 'POST',
                    body: JSON.stringify({
                        imdb_id: imdb_id,
                        title: title,
                        description: description,
                        image: image,
                        imdbRating: imdbRating,
                        imdbVotes: imdbVotes,
                        rating: rating,
                        review: review.value
                    })
                })
                .then(response => {
                    if (response.status === 201) {
                        window.location.reload();
                    };
                    console.log(response.json());
                })
                .catch(error => {
                    reset()
                    console.log(error);
                });
        }

    });
})


function find(event) {
    event.preventDefault();

    // Get input value
    let input = document.querySelector("#title");
    let title = input.value;

    input.value = '';
    input.placeholder = "Loading...";
    document.querySelector("#loading").style.display = 'block';

    // Post email data
    fetch(`https://imdb-api.com/en/API/Search/k_rb56a5ac/${title}`)
        .then(response => response.json())
        .then(data => {
            // Store results as a variable
            var results = data.results;
            // Check if results are empty
            if (results === null) {
                alert("No results found");
                reset();
            } else {
                // Process results
                load_cards(results);
                console.log(results);
                history.pushState({
                    results: results
                }, "", `/search?title=${title}`);
            }
        })
        .catch(error => {
            reset()
            console.log(error);
        });
}

function load_cards(results) {

    const l = Number(results.length);
    var counter = 0;

    Object.entries(results).forEach(([rank, entry]) => {

        // Extract info
        const id = entry.id;

        // Fetch rating
        fetch(`http://www.omdbapi.com/?apikey=3181a075&i=${id}`)
            .then(response => response.json())
            .then(result => {

                let imdbRating = result.imdbRating;
                if (imdbRating === undefined) {
                    imdbRating = "N/A"
                }
                results[`${rank}`]['imdbRating'] = imdbRating;
                let votes = convertToInternationalCurrencySystem(result.imdbVotes);

                if (votes === "remove") {
                    delete results[`${rank}`];
                } else {
                    results[`${rank}`]['imdbVotes'] = votes;
                }

                // Increment counter
                counter++;

                // Check if counter is equal to length of results
                if (counter === l) {
                    post_results(results);
                }
            })
            .catch(error => {
                reset()
                console.log(error);
            });
    });
}


function post_results(values) {
    // Post results
    fetch('/search', {
            method: 'POST',
            body: JSON.stringify({
                results: values
            })
        })
        .then(response => {
            console.log(response.json());
            if (response.status === 201) {
                // Refresh page
                reset();
                history.replaceState({
                    results: values
                }, '');
                window.location.reload();
            }
        })
        .catch(error => {
            reset()
            console.log(error);
        });
}