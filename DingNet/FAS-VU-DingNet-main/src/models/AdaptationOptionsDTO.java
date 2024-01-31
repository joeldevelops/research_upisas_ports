package models;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * This class is a Data Transfer Object wrapping a list of {@code AdaptationOptionModel}s
 * such that the JSON in {@code AdaptationOptionsHandler} and
 * {@code AdaptationOptionsSchemaHandler} is not an array.
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class AdaptationOptionsDTO {
    private List<AdaptationOptionModel> items;
}
