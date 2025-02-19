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
    const response = await fetch("https://07kdlkmc4f.execute-api.us-east-1.amazonaws.com/test", {
      method: "POST",
      headers: { "Content-Type": "application/json"
        },
      body: JSON.stringify({ username, characters, size, fontGroup }),
    });
    const textData = await response.text(); // Read response as text
    try {
        const data = JSON.parse(textData);  // Convert stringified JSON to an object
        const url = JSON.parse(data.body)
        setDownloadLink(url.download_url);
      } catch (error) {
        console.error("Error parsing JSON:", error);
      }
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
