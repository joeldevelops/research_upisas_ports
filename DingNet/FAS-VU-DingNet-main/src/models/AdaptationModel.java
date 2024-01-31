package models;

import lombok.Data;

/**
 * This class implements a model describing an adaptation of DingNet.
 * @version 1.0
 */
@Data
public class AdaptationModel {
    /**
     * The name of the adaptation.
     * @since 1.0
     */
    private String name;

    /**
     * The numerical value of the adaptation.
     * @since 1.0
     */
    private Double value;
}