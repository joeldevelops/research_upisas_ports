package models;

import lombok.Data;

import java.util.List;

/**
 * This class implements a model describing the parameters of executing adaptations.
 * @version 1.0
 */
@Data
public class ExecuteModel {
    /**
     * The ID of the mote to perform adaptations on.
     * @since 1.0
     */
    private Integer id;

    /**
     * The list of adaptation models describing the adaptations to be applied to the mote.
     * @since 1.0
     */
    private List<AdaptationModel> adaptations;
}
