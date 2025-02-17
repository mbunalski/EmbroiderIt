"use client";

import {useState} from "react";
import {TextInput} from "./TextInput";
import {Dropdown} from "./Dropdown";
import {Header} from "./Header";

const fontGroups = ["Floral", "Bold", "Italic"]; // Example options

export function MainForm () {
  const [username, setUsername] = useState("");
  const [characters, setCharacters] = useState("");
  const [size, setSize] = useState("");
  const [fontGroup, setFontGroup] = useState(fontGroups[0]);
  const [downloadLink, setDownloadLink] = useState("");

  const handleSubmit = async () => {
    const response = await fetch("https://cyw8e6y685.execute-api.us-east-1.amazonaws.com/default/embroiderit-generate", {
      method: "POST",
      headers: { "Content-Type": "application/json",
      "Access-Control-Allow-Origin" : "*", // Required for CORS support to work
      "Access-Control-Allow-Credentials" : true // Required for cookies, authorization headers with HTTPS},
        },
      body: JSON.stringify({ username, characters, size, fontGroup }),
    });
    const data = await response.json();
    setDownloadLink(data.download_url);
  };

  const handleCopyLink = () => {
    if (downloadLink) {
      navigator.clipboard.writeText(downloadLink);
      alert("Link copied!");
    }
  };

  return (
    <div className="p-4 max-w-md mx-auto">
      <Header title="EmbroiderIt"/>
      <TextInput label="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <TextInput label="Characters" value={characters} onChange={(e) => setCharacters(e.target.value)} />
      <TextInput label="Size" value={size} onChange={(e) => setSize(e.target.value)} />
      <Dropdown label="Font Group" options={fontGroups} value={fontGroup} onChange={(e) => setFontGroup(e.target.value.toLowerCase())} />
      
      <button onClick={handleSubmit} className="mt-4 p-2 bg-blue-500 text-white rounded">Submit</button>
      {downloadLink && (
        <button onClick={handleCopyLink} className="mt-4 ml-2 p-2 bg-green-500 text-white rounded">Copy Link</button>
      )}
    </div>
  );
};

export default MainForm;
