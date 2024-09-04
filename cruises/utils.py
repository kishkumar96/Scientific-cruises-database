from django.contrib.gis.geos import LineString, Point, MultiLineString

def wrap_longitude(lon):
    """ Normalize longitude to the -180 to 180 range. """
    return (lon + 180) % 360 - 180

def antimeridian_split(line_string):
    """ Splits a LineString at the antimeridian (+180 or -180 longitude) """
    new_coords = []
    split_lines = []
    previous_point = line_string.coords[0]

    for current_point in line_string.coords[1:]:
        new_coords.append((previous_point[0], previous_point[1]))
        if abs(previous_point[0] - current_point[0]) > 180:  # Crossing detected
            # Calculate the latitude at the antimeridian
            mid_lat = (previous_point[1] + current_point[1]) / 2
            # Longitude sign determines which meridian is crossed
            meridian = 180 if previous_point[0] > 0 else -180
            # Add the crossing point to the current line
            new_coords.append((meridian, mid_lat))
            # Start a new line after the crossing
            split_lines.append(LineString(new_coords))
            new_coords = [(wrap_longitude(meridian), mid_lat), (current_point[0], current_point[1])]
        previous_point = current_point

    if new_coords:
        split_lines.append(LineString(new_coords))

    return split_lines

def create_multilinestring_from_splits(splits):
    """ Create a MultiLineString from split LineStrings if necessary. """
    # Ensure always returning a MultiLineString regardless of the number of splits
    if not splits:
        return MultiLineString()
    elif len(splits) == 1:
        # If there's only one split, wrap it in a MultiLineString
        return MultiLineString(splits[0])
    else:
        return MultiLineString(*splits)