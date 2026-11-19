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

for (const item of likeButtons) {
    item.addEventListener('click', () => {
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
            .catch((error) => {
                alert(error.message);
            })
            .finally(() => {
                item.disabled = false;
            });
    });
}

for (const item of correctButtons) {
    item.addEventListener('click', () => {
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
}