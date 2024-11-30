from loguru import logger


class SQLSymphonyException(Exception):
    """
    Exception for signaling sql symphony errors.
    """

    def __init__(self, *args):
        """
        Constructs a new instance.

        :param		args:  The arguments
        :type		args:  list
        """
        if args:
            self.message = args[0]
        else:
            self.message = None

    def get_explanation(self) -> str:
        """
        Gets the explanation.

        :returns:	The explanation.
        :rtype:		str
        """
        return f"Basic SQLSymphony ORM exception. Message: {self.message if self.message else 'missing'}"

    def __str__(self):
        """
        Returns a string representation of the object.

        :returns:	String representation of the object.
        :rtype:		str
        """
        logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
        return f"SQLSymphonyException has been raised. {self.get_explanation()}"


class FieldNamingError(SQLSymphonyException):
    """
    This class describes a field naming error.
    """

    def __init__(self, *args):
        """
        Constructs a new instance.

        :param		args:  The arguments
        :type		args:  list
        """
        if args:
            self.message = args[0]
        else:
            self.message = None

    def get_explanation(self) -> str:
        """
        Gets the explanation.

        :returns:	The explanation.
        :rtype:		str
        """
        return f"SQLSymphony Field Naming Error. The field name is prohibited/unavailable to avoid naming errors. Message: {self.message if self.message else 'missing'}"

    def __str__(self):
        logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
        return f"Field Naming Error has been raised. {self.get_explanation()}"


class NullableFieldError(SQLSymphonyException):
    """
    This class describes a nullable field error.
    """

    def __init__(self, *args):
        """
        Constructs a new instance.

        :param		args:  The arguments
        :type		args:  list
        """
        if args:
            self.message = args[0]
        else:
            self.message = None

    def get_explanation(self) -> str:
        """
        Gets the explanation.

        :returns:	The explanation.
        :rtype:		str
        """
        return f"SQLSymphony Nullable Field Error. Field is set to NOT NULL, but it is empty. Message: {self.message if self.message else 'missing'}"

    def __str__(self):
        logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
        return f"Nullable Field Error has been raised. {self.get_explanation()}"


class FieldValidationError(SQLSymphonyException):
    """
    This class describes a field validation error.
    """

    def __init__(self, *args):
        """
        Constructs a new instance.

        :param		args:  The arguments
        :type		args:  list
        """
        if args:
            self.message = args[0]
        else:
            self.message = None

    def get_explanation(self) -> str:
        """
        Gets the explanation.

        :returns:	The explanation.
        :rtype:		str
        """
        return f"SQLSymphony Field Validation Error. Message: {self.message if self.message else 'missing'}"

    def __str__(self):
        logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
        return f"Field Validation Error has been raised. {self.get_explanation()}"


class PrimaryKeyError(SQLSymphonyException):
    """
    This class describes a primary key error.
    """

    def __init__(self, *args):
        """
        Constructs a new instance.

        :param		args:  The arguments
        :type		args:  list
        """
        if args:
            self.message = args[0]
        else:
            self.message = None

    def get_explanation(self) -> str:
        """
        Gets the explanation.

        :returns:	The explanation.
        :rtype:		str
        """
        return f"SQLSymphony Primary Key Error. According to database theory, each table should have only one PrimaryKey field, Message: {self.message if self.message else 'missing'}"

    def __str__(self):
        logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
        return f"Primary Key Error has been raised. {self.get_explanation()}"


class UniqueConstraintError(SQLSymphonyException):
    """
    This class describes an unique constraint error.
    """

    def __init__(self, *args):
        """
        Constructs a new instance.

        :param		args:  The arguments
        :type		args:  list
        """
        if args:
            self.message = args[0]
        else:
            self.message = None

    def get_explanation(self) -> str:
        """
        Gets the explanation.

        :returns:	The explanation.
        :rtype:		str
        """
        return f"SQLSymphony Unique Constraint Error. An exception occurred when executing an SQL query due to problems with UNIQUE fields. Message: {self.message if self.message else 'missing'}"

    def __str__(self):
        logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
        return f"Unique Constraint Error has been raised. {self.get_explanation()}"


class ModelHookError(SQLSymphonyException):
    """
    This class describes a model hook error.
    """

    def __init__(self, *args):
        """
        Constructs a new instance.

        :param		args:  The arguments
        :type		args:  list
        """
        if args:
            self.message = args[0]
        else:
            self.message = None

    def get_explanation(self) -> str:
        """
        Gets the explanation.

        :returns:	The explanation.
        :rtype:		str
        """
        return f"Model Hooks Error. An exception occurred when executing an hook due to problems with ORM. Message: {self.message if self.message else 'missing'}"

    def __str__(self):
        logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
        return f"Model Hook error has been raised. {self.get_explanation()}"


class MigrationError(SQLSymphonyException):
    """
    This class describes a migration error.
    """

    def __init__(self, *args):
        """
        Constructs a new instance.

        :param		args:  The arguments
        :type		args:  list
        """
        if args:
            self.message = args[0]
        else:
            self.message = None

    def get_explanation(self) -> str:
        """
        Gets the explanation.

        :returns:	The explanation.
        :rtype:		str
        """
        return f"Database Migration Error. An exception occurred when executing an hook due to problems with migration. Message: {self.message if self.message else 'missing'}"

    def __str__(self):
        logger.error(f"{self.__class__.__name__}: {self.get_explanation()}")
        return f"Migration Error has been raised. {self.get_explanation()}"
