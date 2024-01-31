package HTTP;

import com.fasterxml.jackson.databind.JsonNode;
import com.github.victools.jsonschema.generator.*;
import com.github.victools.jsonschema.module.jackson.JacksonModule;

/**
 * This class implements the JSON schema for the schema endpoints monitor_schema,
 * adaptation_option_schema, and execute_schema.
 * @version 1.0
 */
public class Schema {

    /**
     * Returns a JSON schema of the object in {@code clazz} as {@code String}.
     * @param clazz The object to be converted into a JSON schema.
     * @return A JSON schema of the object in {@code clazz} as {@code String}.
     * @exception RuntimeException if the object {@code clazz} could not be represented as JSON schema
     * @since 1.0
     */
    public static String toJsonSchema(Class<?> clazz) {
        try {
            SchemaGeneratorConfigBuilder configBuilder = new SchemaGeneratorConfigBuilder(
                        SchemaVersion.DRAFT_2020_12,
                        OptionPreset.PLAIN_JSON
            );

            SchemaGeneratorConfig config = configBuilder.with(new JacksonModule()).build();
            SchemaGenerator generator = new SchemaGenerator(config);
            JsonNode jsonSchema = generator.generateSchema(clazz);

            return jsonSchema.toPrettyString();
        } catch (Exception e) {
            throw new RuntimeException(e.getMessage());
        }
    }
}
