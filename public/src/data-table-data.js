import "./css/data-table.css";
import React from "react";
import ModalImage from "react-modal-image";
import DataTableAddTags from "./data-table-add-tags";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const DataTableData = props => {
  const {
    record = {},
    handleUpdate,
    handleGetTagSuggestions,
    tagSuggestions,
    handleReprocessRecord
  } = props;

  const handleDeleteTag = (tag, recordItem) => {
    handleUpdate({ tags: [tag], recordItem, updateMode: "remove_tag" }); // pass back through function prop
  };

  const handleRotateImage = (recordItem, degrees) => {
    handleUpdate({
      recordItem,
      updateMode: "rotate_image",
      updateParams: { rotation_degrees: degrees }
    }); // pass back through function prop
  };

  const handleReprocess = ({ record = null } = {}) => {
    handleReprocessRecord({ record });
  };

  return record.data.results.map((item, index) => {
    let { file_format, file_name, tags, public_img_tn_url, uuid } = item;
    let rowClasses = ["d-flex", "dataTableRows"];
    let imgClasses = [
      "img-fluid",
      "img-thumbnail",
      "d-block",
      "mx-auto",
      "card-img-top"
    ];
    let small_img_url = `${process.env.REACT_APP_ROUTE}${public_img_tn_url}/${file_name}-350_350${file_format}?${uuid}`;
    let medium_img_url = `${process.env.REACT_APP_ROUTE}${public_img_tn_url}/${file_name}-720_720${file_format}`;
    let full_img_url = `${process.env.REACT_APP_ROUTE}${public_img_tn_url}/${file_name}-1080_1080${file_format}`;
    return (
      <tr
        key={`data-table-tags-${item.id}`}
        data-toggle="modal"
        className={rowClasses.join(" ")}
      >
        {/*<th scope="row">{item.id}</th>*/}
        <td className={"col-3 photo"}>
          <div className={"card bg-info"}>
            <ModalImage
              small={small_img_url}
              medium={medium_img_url}
              large={full_img_url}
              alt={tags.join(", ")}
              className={imgClasses.join(" ")}
            />
            <div className={"card-footer"}>
              <div
                className={"btn-toolbar"}
                role={"toolbar"}
                aria-label={"Photo mutation toolbar"}
              >
                <div
                  className={"btn-group"}
                  role={"group"}
                  aria-label={"Group 1"}
                >
                  <button
                    disabled={!item.user_is_admin}
                    onClick={() => handleRotateImage(item, 90)}
                    className={"btn btn-sm btn-warning"}
                  >
                    <FontAwesomeIcon icon={"undo"} />
                  </button>
                  <button
                    disabled={!item.user_is_admin}
                    onClick={() => handleRotateImage(item, -90)}
                    className={"btn btn-sm btn-warning ml-1"}
                  >
                    <FontAwesomeIcon icon={"redo"} />
                  </button>
                  <button
                    disabled={!item.user_is_admin}
                    onClick={() => handleReprocess({record: item})}
                    className={"btn btn-sm btn-warning ml-1"}
                  >
                    <FontAwesomeIcon icon={"sync-alt"} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </td>
        <td className={"col-5 tags"}>
          <ul>
            {tags.map((tag, key) => (
              <li key={`data-table-tags-${key}`}>
                <span className={"badge badge-pill badge-warning text-wrap"}>
                  {tag}
                  <button
                    className={"btn btn-sm btn-danger m-1"}
                    onClick={() => handleDeleteTag(tag, item)}
                  >
                    <FontAwesomeIcon icon={"trash-alt"} />
                  </button>
                </span>
              </li>
            ))}
          </ul>
        </td>
        <td className={"action-col col-4 text-center"}>
          <DataTableAddTags
            handleUpdate={handleUpdate}
            handleGetTagSuggestions={handleGetTagSuggestions}
            recordItem={item}
            existingTags={tags}
            tagSuggestions={tagSuggestions}
          />
        </td>
      </tr>
    );
  });
};
export default DataTableData;

/*
Note 1: Be sure to pass values (e.g. {...item}) rather than obj (e.g. {item}),
otherwise the item obj (corresponding to the data results on the main table) will be updated with
values input in the console, as data.updateData would essentially
point to data.results, rather than being a separate, discrete object.
 */
