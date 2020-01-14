import "./css/data-table.css";
import React from "react";
import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const DataTableAddTags = props => {
  let {
    handleUpdate,
    handleGetTagSuggestions,
    recordItem,
    existingTags,
    tagSuggestions
  } = props;

  const [tags, setTags] = useState(""); // initial value

  const staticTagSuggestionBlacklist = ["SPM: TAGS COPIED FROM ORIGINAL"];
  const tagSuggestionBlacklist = staticTagSuggestionBlacklist.concat(
    existingTags
  );

  const _validateInput = value => {
    return /^[a-zA-Z\d\-/():'?| ]*$/.test(value) ? value : tags;
  };

  const handleChangeTags = e => {
    /* validate input */
    const validatedInput = _validateInput(e.target.value);
    /* get existing tags matching term currently** being typed [**hence split at '/'] */
    let activeTerm = validatedInput.split("/").pop();
    handleGetTagSuggestions({ term: activeTerm, itemID: recordItem.id });
    /* set tags in state */
    setTags(validatedInput);
  };

  const handleSubmit = event => {
    event.preventDefault();
    if (tags) {
      handleUpdate({
        tags: tags.split("/"),
        recordItem,
        updateMode: "add_tags"
      }); // pass back through function prop
      setTags(""); // clear state
    }
  };

  const handleChooseSuggestion = (e, tag) => {
    e.preventDefault();
    handleUpdate({
      tags: [tag],
      recordItem,
      updateMode: "add_tags"
    });
    let currentTags = tags.split("/");
    currentTags.pop();
    currentTags.length ? setTags(`${currentTags.join("/")}/`) : setTags("");
    handleGetTagSuggestions({ term: "", itemID: recordItem.id }); // reset suggestions
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className={"form-row"}>
        <div className={"col-sm-8 col-md-9 col-7"}>
          <input
            type={"text"}
            value={tags}
            onChange={handleChangeTags}
            className={"form-control"}
            disabled={!recordItem.user_is_admin}
            placeholder={"new tag 1/new tag 2"}
          />
          <div className={"searchSuggestions"}>
            <ul>
              {/* map tag suggestions to list but omit entries in blacklist */
              tagSuggestions.itemID === recordItem.id
                ? tagSuggestions.suggestions.map((tag, key) =>
                    tagSuggestionBlacklist.includes(tag) ? null : (
                      <li key={`suggestions-${key}`}>
                        <span
                          className={
                            "tagSuggestions badge badge-pill badge-primary text-wrap"
                          }
                        >
                          {tag}
                          <button
                            className={"btn btn-sm btn-success m-1"}
                            onClick={e => handleChooseSuggestion(e, tag)}
                          >
                            <FontAwesomeIcon icon={"plus"} />
                          </button>
                        </span>
                      </li>
                    )
                  )
                : ""}
            </ul>
          </div>
        </div>
        <div className={"col-sm-4 col-md-3 col-5"}>
          <button
            type={"submit"}
            value={"submit"}
            disabled={!recordItem.user_is_admin}
            className={"btn btn-md btn-warning"}
          >
            <FontAwesomeIcon icon={"plus"} />
          </button>
        </div>
      </div>
    </form>
  );
};

export default DataTableAddTags;
