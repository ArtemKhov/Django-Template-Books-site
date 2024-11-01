document.addEventListener('DOMContentLoaded', function() {
 const likedImagePath = document.querySelector('body').getAttribute('data-liked-image-url');
 const notLikedImagePath = document.querySelector('body').getAttribute('data-not-liked-image-url');

 document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

            fetch(`/comment/${commentId}/like/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.liked) {
                this.querySelector('img').src = likedImagePath;
            } else {
                this.querySelector('img').src = notLikedImagePath;
            }
            const likeCountElement = this.querySelector('.like-count');
            if (likeCountElement) {
                likeCountElement.innerText = data.likes_count;
            } else {
                console.error('Элемент обновления количества лайков не найден.');
            }
        })
        .catch(error => console.error('Error:', error));
        });
    });
});