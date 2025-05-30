
const postContainer = document.getElementById("post-container");


fetch("/api/posts")
    .then(response => response.json())
    .then(data => {
        postContainer.innerHTML = "";

        data.forEach(post => {
        const div = document.createElement("div");
        console.log("image path: ", post.image_path);

        div.innerHTML = `
            <a href="view-post/${post.post_id}">
                <div class="post">
                    <h3 class="post-title">${post.title}</h3>
                    <img src="/static/uploads/${post.post_id}.jpg" alt="(picture)" class="post-img">
                    <p class="post-found">Found: ${post.date_found}</p>
                </div>
            </a>
        `;
        postContainer.appendChild(div);
    });
});
