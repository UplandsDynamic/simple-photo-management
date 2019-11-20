import React from "react";
import "bootstrap/dist/css/bootstrap.css";
import "bootstrap/dist/js/bootstrap.js";
import moment from "moment";
import "moment/locale/en-gb.js";
import "moment-timezone";
import DataTableNav from "./data-table-nav";
import DataTableData from "./data-table-data";
import DataTableHead from "./data-table-head";
import "./css/data-table.css";

const DataTable = props => {
  const {
    record = {},
    getRecordsHandler,
    handleGetTagSuggestions,
    authMeta = {},
    handleProcessPhotos,
    handleUpdate,
    handleSearchAndReplace,
    tagSuggestions,
  } = props;

  const _formatUTCDateTime = ({ dateTime = null } = {}) => {
    // takes datetime in UTC, formats and returns datetime in user's browser reported timezone
    return dateTime
      ? `${moment
          .utc(dateTime)
          .local()
          .format("DD/MM/YYYY HH:mm:ss")} ${moment
          .tz(moment.tz.guess())
          .zoneAbbr()}`
      : null;
  };

  const handleColumnOrderChange = ({ record = {}, newOrder = {} } = {}) => {
    let { pageOrderDir, pageOrderBy } = record.meta;
    // set page order direction
    pageOrderDir = !pageOrderBy || pageOrderDir === "-" ? "" : "-"; // *see note 1
    Object.assign(record.meta, {
      pageOrderBy: newOrder,
      pageOrderDir,
      page: 1
    }); // maybe page:1 ?
    getRecordsHandler({ record });
  };

  const handleSearch = ({ record = {}, term = null } = {}) => {
    if (record) {
      Object.assign(record.meta, {
        pageOrderBy: "record_updated",
        pageOrderDir: "-",
        page: 1,
        search: term
      });
      // get the matching records from the API
      setTimeout(function() {
        getRecordsHandler({ record });
      }, 1000);
      //getRecordsHandler({ record });
    }
  };

  const DataTableDataWrapper = () => (
    <DataTableData
      record={record}
      handleUpdate={handleUpdate}
      handleGetTagSuggestions={handleGetTagSuggestions}
      tagSuggestions={tagSuggestions}
    />
  );

  const noDataWrapper = () => (
    <tr data-toggle="modal" className={"d-flex dataTableRows"}>
      <td className={"col-12 no-data"}>
        <div className={"alert alert-warning"}>
          No data to display. Please search for records!
        </div>
      </td>
    </tr>
  );

  return (
    <div className={"data-table"}>
      <DataTableNav
        record={record}
        handleGetRecords={getRecordsHandler}
        handleProcessPhotos={handleProcessPhotos}
        handleSearch={handleSearch}
        handleSearchAndReplace={handleSearchAndReplace}
        authMeta={authMeta}
      />
      <div className={"container"}>
        <div className={"row"}>
          <div className={"col-sm table-responsive table-sm"}>
            <table className="table table-bordered table-dark table-hover">
              <caption>
                Archived Images
                {record.meta.datetime_of_request
                  ? `[Request returned:
                                        ${_formatUTCDateTime({
                                          dateTime:
                                            record.meta.datetime_of_request
                                        })}]`
                  : ""}
              </caption>
              <thead>
                <DataTableHead
                  record={record}
                  handleColumnOrderChange={handleColumnOrderChange}
                />
              </thead>
              <tbody>
                {record.data.results.length > 0 && authMeta.authenticated
                  ? DataTableDataWrapper()
                  : noDataWrapper()}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataTable;
