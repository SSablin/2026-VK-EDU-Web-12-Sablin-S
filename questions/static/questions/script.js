function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');
const likeButtons = document.querySelectorAll('button[data-like-url]');
const correctButtons = document.querySelectorAll('button[data-correct-url]');

function updateLikeButtons(item, isLike) {
    const buttons = document.querySelectorAll(
        `button[data-like-id="${item.dataset.likeId}"]`
    );
    for (const button of buttons) {
        const active = (button.dataset.likeType === 'like' && isLike === true)
            || (button.dataset.likeType === 'dislike' && isLike === false);
        const isLikeButton = button.dataset.likeType === 'like';
        button.classList.toggle('btn-success', active && isLikeButton);
        button.classList.toggle('btn-outline-success', !active && isLikeButton);
        button.classList.toggle('btn-danger', active && !isLikeButton);
        button.classList.toggle('btn-outline-danger', !active && !isLikeButton);
    }
}

document.addEventListener('click', (event) => {
    const item = event.target.closest('button[data-like-url]');
    if (!item) {
        return;
    }

    const counter = document.querySelector(
        `span[data-like-counter="${item.dataset.likeId}"]`
    );
    item.disabled = true;

    fetch(item.dataset.likeUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        mode: 'same-origin',
        body: JSON.stringify({ type: item.dataset.likeType }),
    })
        .then((response) => response.json().then((data) => ({
            ok: response.ok,
            data: data,
        })))
        .then((result) => {
            if (!result.ok) {
                throw new Error(result.data.error);
            }
            counter.innerText = result.data.rating;
            updateLikeButtons(item, result.data.is_like);
        })
        .catch((error) => alert(error.message))
        .finally(() => {
            item.disabled = false;
        });
});

document.addEventListener('click', (event) => {
    const item = event.target.closest('button[data-correct-url]');
    if (!item) {
        return;
    }

    item.disabled = true;

    fetch(item.dataset.correctUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        mode: 'same-origin',
        body: JSON.stringify({ type: item.dataset.correctType }),
    })
        .then((response) => response.json().then((data) => ({
            ok: response.ok,
            data: data,
        })))
        .then((result) => {
            if (!result.ok) {
                throw new Error(result.data.error);
            }
            const buttons = document.querySelectorAll(
                `button[data-correct-question="${item.dataset.correctQuestion}"]`
            );
            for (const button of buttons) {
                const isCorrect = button === item && result.data.is_correct;
                button.dataset.correctType = isCorrect ? 'incorrect' : 'correct';
                button.classList.toggle('btn-success', isCorrect);
                button.classList.toggle('btn-outline-success', !isCorrect);
            }
        })
        .catch((error) => {
            alert(error.message);
        })
        .finally(() => {
            item.disabled = false;
        });
});

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('header-search-input');
    const suggestionsBox = document.getElementById('search-suggestions');
    if (!searchInput || !suggestionsBox) return;

    function debounce(fn, delay) {
        let timerId;
        return function (...args) {
            clearTimeout(timerId);
            timerId = setTimeout(() => fn.apply(this, args), delay);
        };
    }

    const fetchSuggestions = async (query) => {
        if (query.trim().length < 2) {
            suggestionsBox.style.display = 'none';
            suggestionsBox.innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/search/suggestions/?q=${encodeURIComponent(query)}`);
            if (!response.ok) return;
            const data = await response.json();

            if (data.suggestions.length === 0) {
                suggestionsBox.style.display = 'none';
                return;
            }

            suggestionsBox.innerHTML = data.suggestions.map(item => `
                <a href="${item.url}" class="list-group-item list-group-item-action">
                    ${item.title}
                </a>
            `).join('');
            suggestionsBox.style.display = 'block';
        } catch (err) {
            console.error('Search error:', err);
        }
    };

    searchInput.addEventListener('input', debounce((e) => {
        fetchSuggestions(e.target.value);
    }, 300));

    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = 'none';
        }
    });
});
