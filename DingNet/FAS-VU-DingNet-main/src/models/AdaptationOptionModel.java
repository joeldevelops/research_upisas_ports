package models;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Data;

/**
 * This class implements a model describing the options for a DingNet adaptation.
 * Only non-null values are included when an instance of this class is mapped to JSON.
 * @version 1.0
 */
@Data
@AllArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class AdaptationOptionModel {
    /**
     * The name of the adaptation.
     * @since 1.0
     */
    private String name;

    /**
     * A textual description of the adaptation.
     * @since 1.0
     */
    private String description;

    /**
     * The minimum numerical value of the adaptation.
     * @since 1.0
     */
    private Double minValue;

    /**
     * The maximum numerical value of the adaptation.
     * @since 1.0
     */
    private Double maxValue;
}
