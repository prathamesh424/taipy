import React, { useState } from "react";

const DateTimeValidator: React.FC = () => {
  const [dateTime, setDateTime] = useState<string>("");
  const [error, setError] = useState<string>("");

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setDateTime(value);
    validateTime(value);
  };

  const validateTime = (value: string) => {
    if (!value) return;

    const time = new Date(value);
    const minutes = time.getMinutes();

    // Check if minutes are a multiple of 15
    if (minutes % 15 !== 0) {
      setError("Time must be in 15-minute increments.");
    } else {
      setError("");
    }
  };

  return (
    <div>
      <label htmlFor="datetime">Choose date and time:</label>
      <input
        type="datetime-local"
        id="datetime"
        value={dateTime}
        onChange={handleChange}
        step={900} // Allows 15-minute steps (900 seconds)
      />
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default DateTimeValidator;
