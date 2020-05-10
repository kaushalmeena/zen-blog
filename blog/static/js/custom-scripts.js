function searchPosts(route = "/", page = 1) {
  var params = {
    page
  };
  var input = document.getElementById("search");
  if (input) {
    params.query = input.value;
  }
  var queryString = Object.keys(params)
    .map(function (key) {
      return key + '=' + params[key];
    })
    .join('&');

  window.location = route + '?' + queryString;
}

function detectEnterKeyPress(e) {
  if (e.keyCode === 13) {
    e.preventDefault();
    searchPosts()
  }
}

function deletePost(postId) {
  if (confirm("Do you really want to delete this post?")) {
    window.location = '/post/' + postId + '/delete';
  }
}

function deleteComment(commentId) {
  if (confirm("Do you really want to delete this comment?")) {
    window.location = '/comment/' + commentId + '/delete';
  }
}