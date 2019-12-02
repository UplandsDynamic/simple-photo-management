import "./css/data-table.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import Paginate from "./paginate.js";
import React from "react";
import { useState } from "react";

const DataTableNav = props => {
  const {
    record = {},
    authMeta = {},
    handleGetRecords,
    handleProcessPhotos,
    handleSearch,
    handleSearchAndReplace,
    handlePruneTags,
  } = props;
  const [term, setTerm] = useState(""); // initial value
  const [replaceTerm, setReplaceTerm] = useState("");
  const [sar, setSar] = useState(false);
  const userIsAdmin = authMeta.userIsAdmin;

  const validateTerm = value => {
    return /^[a-zA-Z\d./+\-'?:"| ]*$/.test(value) ? value : term;
  };

  const handleProcessClick = ({
    scan = false,
    retag = false,
    clean_db = false
  } = {}) => {
    handleProcessPhotos({ scan, retag, clean_db });
  };

  const searchAndReplaceSwitch = () => {
    setSar(!sar);
    resetTerms();
  };

  const resetTerms = () => {
    setTerm("");
    setReplaceTerm("");
  };

  const handleChange = e => {
    if (!sar) {
      // if not search & replace (sar), handleSearch to fetch records
      handleSearch({ record, term: validateTerm(e.target.value) });
    }
    setTerm(validateTerm(e.target.value)); // update term in state whether sar or not
  };

  const handleReplaceChange = e => {
    setReplaceTerm(validateTerm(e.target.value)); // update term in state whether sar or not
  };

  const handleReplace = () => {
    handleSearchAndReplace({
      searchTerm: term,
      replaceTerm: replaceTerm
    });
    resetTerms(); // reset both search & replace terms
  };

  const pruneTags = () => {
    handlePruneTags();
  };

  const getRecords = () => {
    Object.assign(record.meta, { page: 1 });
    handleGetRecords({ record });
  };

  return (
    <div className={"container"}>
      <div className={"row nav-row"}>
        <div className={"col-12"}>
          <div className={"btn-group float-right"}>
            <nav
              className="nav-pagination float-right"
              aria-label="Table data pages"
            >
              <Paginate record={record} handleGetRecords={handleGetRecords} />
            </nav>
          </div>
        </div>
      </div>
      <div className={"row nav-row"}>
        <div className={`${userIsAdmin ? "col-4" : "col-2"}`}>
          <div className={"btn-group"}>
            <button
              onClick={getRecords}
              className={"btn btn-md btn-success mr-1 "}
            >
              <FontAwesomeIcon icon={"sync-alt"} />
            </button>
            <button
              onClick={() => handleProcessClick({ scan: true })}
              className={`btn btn-md btn-warning mr-1`}
            >
              <FontAwesomeIcon icon={"plus"} />
            </button>
            <button
              onClick={
                userIsAdmin ? () => handleProcessClick({ retag: true }) : null
              }
              className={`btn btn-md btn-warning mr-1 ${
                !userIsAdmin ? "disabled" : ""
              }`}
            >
              <FontAwesomeIcon icon={"tags"} />
            </button>
            <button
              onClick={
                userIsAdmin
                  ? () => handleProcessClick({ clean_db: true })
                  : null
              }
              className={`btn btn-md btn-warning mr-1 ${
                !userIsAdmin ? "disabled" : ""
              }`}
            >
              <FontAwesomeIcon icon={"broom"} />
            </button>
            <button
              onClick={userIsAdmin ? pruneTags : null}
              className={`btn btn-md btn-warning mr-1 ${
                !userIsAdmin ? "disabled" : ""
              }`}
            >
              <FontAwesomeIcon icon={"remove-format"} />
            </button>
            <button
              onClick={userIsAdmin ? searchAndReplaceSwitch : null}
              className={`btn btn-md btn-warning mr-1 ${
                !userIsAdmin ? "disabled" : ""
              }`}
            >
              <FontAwesomeIcon icon={"exchange-alt"} />
            </button>
          </div>
        </div>
        <div className={`col-8`}>
          <nav className={"search-navigation w-100 d-block ml-1"}>
            <input
              value={term}
              placeholder={"Search"}
              name={"search"}
              className={"form-control search"}
              onChange={handleChange}
            />
            {sar ? (
              <div className={"searchAndReplace"}>
                <input
                  value={replaceTerm}
                  placeholder={"Replace"}
                  name={"replace"}
                  className={"form-control replace"}
                  onChange={handleReplaceChange}
                />
                {term && replaceTerm ? (
                  <button
                    onClick={userIsAdmin ? handleReplace : null}
                    className={`btn btn-lg btn-danger float-right ${
                      !userIsAdmin ? "disabled" : ""
                    }`}
                  >
                    <FontAwesomeIcon icon={"exchange-alt"} className={"mr-2"} />
                    {term && replaceTerm
                      ? `Replace all "${term}" tags with "${replaceTerm}" ?`
                      : ""}
                  </button>
                ) : (
                  ""
                )}
              </div>
            ) : null}
          </nav>
        </div>
      </div>
    </div>
  );
};
export default DataTableNav;
