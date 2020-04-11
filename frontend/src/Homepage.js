import React, {useState, useEffect, Fragment} from "react";
import ReactDOM from "react-dom";

function App() {
	return (
		<h1>Welcome to the jobhound!</h1>
	)
}

const wrapper = document.getElementById("app");
wrapper ? ReactDOM.render(<App/>, wrapper) : null;