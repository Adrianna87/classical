// let baseURL = "https://api.openopus.org";
// async function search() {
// evt.preventDefault();

// let inputVal = document.getElementById("search").value;
// console.log(inputVal);

// const composer = await $.getJSON(`${baseURL}/composer/list/search/${search}.json`);
// $("#search").trigger("reset");
// }
console.log("hello")

function makePlaylist(e) {
  console.log(e.target.id);
}

$("#works").on("click", "button", makePlaylist)