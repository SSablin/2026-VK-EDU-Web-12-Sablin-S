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
                item.dataset.correctType = result.data.is_correct ? 'incorrect' : 'correct';
                item.classList.toggle('btn-success', result.data.is_correct);
                item.classList.toggle('btn-outline-success', !result.data.is_correct);
            })
            .catch((error) => {
                alert(error.message);
            })
            .finally(() => {
                item.disabled = false;
            });
    });
}