export function TextInput({ label, value, onChange, placeholder }){

    return(
        <div className="mb-4">
        <label className="block text-sm font-medium">{label}</label>
        <input
          type="text"
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className="mt-1 p-2 border rounded w-full"
        />
      </div>
    );

}



  