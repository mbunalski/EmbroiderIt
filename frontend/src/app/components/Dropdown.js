export function Dropdown ({ label, options, value, onChange }) {
    return (
      <div className="mb-4">
        <label className="block text-sm font-medium">{label}</label>
        <select
          value={value}
          onChange={onChange}
          className="mt-1 p-2 border rounded w-full"
        >
          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>
    );
  };
  