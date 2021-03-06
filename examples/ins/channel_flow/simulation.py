"""User-defined module for simulation."""

import numpy


def set_initial_velocity(gridc, gridx, gridy, ivar, pres):
    """Set the initial velocity field.

    The x- and y-components of the velocity are set to 1.0 and 0.0,
    respectively.

    Arguments
    ---------
    gridx : flowx.Grid object
        Grid containing x-face data.
    gridy : flowx.Grid object
        Grid containing y-face data.
    ivar : string
        Name of the velocity variable on the grid.

    """

    u = gridx.get_values(ivar)
    v = gridy.get_values(ivar)
    p = gridc.get_values(pres)

    u[:, :] = 1.0
    v[:, :] = 0.0
    p[:, :] = 0.0

    return


def get_qin(grid, ivar, bc_type):
    """Compute and return the mass getting in the domain.

    Arguments
    ---------
    grid : flowx.Grid object
        Grid containing data.
    ivar : string
        Name of the velocity variable on the grid.
    bctype : dictionary
        Type of boundary conditions for the variable `ivar`.

    Returns
    -------
    Qin : float
        Mass getting in the domain.

    """
    vel = grid.get_values(ivar)
    dx, dy = grid.dx, grid.dy

    Qin = 0.0

    if grid.type_ is 'x-face':
        if bc_type[0] is not 'outflow':
            Qin += numpy.sum(vel[0, 1:-1]) * dy
        if bc_type[1] is not 'outflow':
            Qin -= numpy.sum(vel[-1, 1:-1]) * dy
    elif grid.type_ is 'y-face':
        if bc_type[2] is not 'outflow':
            Qin += numpy.sum(vel[1:-1, 0]) * dx
        if bc_type[3] is not 'outflow':
            Qin -= numpy.sum(vel[1:-1, -1]) * dx

    return Qin


def get_qout(grid, ivar, bc_type):
    """Compute and return the mass getting out the domain.

    Arguments
    ---------
    grid : flowx.Grid object
        Grid containing data.
    ivar : string
        Name of the velocity variable on the grid.
    bctype : dictionary
        Type of boundary conditions for the variable `ivar`.

    Returns
    -------
    Qout : float
        Mass getting out the domain.

    """
    vel = grid.get_values(ivar)
    dx, dy = grid.dx, grid.dy

    Qout = 0.0

    if grid.type_ is 'x-face':
        if bc_type[0] is 'outflow':
            Qout -= numpy.sum(vel[0, 1:-1]) * dy
        if bc_type[1] is 'outflow':
            Qout += numpy.sum(vel[-1, 1:-1]) * dy
    elif grid.type_ is 'y-face':
        if bc_type[2] is 'outflow':
            Qout -= numpy.sum(vel[1:-1, 0]) * dx
        if bc_type[3] is 'outflow':
            Qout += numpy.sum(vel[1:-1, -1]) * dx

    return Qout


def rescale_velocity(grid, ivar, bc_type, Qin, Qout):
    """Rescale velocity.

    Arguments
    ---------
    grid : flowx.Grid object
        Grid containing data.
    ivar : string
        Name of the velocity variable on the grid.
    bctype : dictionary
        Type of boundary conditions for the variable `ivar`.
    Qin : float
        Mass in.
    Qout : float
        Mass out.

    """
    vel = grid.get_values(ivar)

    Qinout = 1.0
    if Qout > 0.0:
        Qinout = Qin/Qout

    if grid.type_ is 'x-face':
        if bc_type[0] is 'outflow':
            vel[0, 1:-1] *= Qinout
        if bc_type[1] is 'outflow':
            vel[-1, 1:-1] *= Qinout

    if grid.type_ is 'y-face':
        if bc_type[2] is 'outflow':
            vel[1:-1, 0] *= Qinout
        if bc_type[3] is 'outflow':
            vel[1:-1, -1] *= Qinout

    return


def get_convvel(grid, ivar):
    """Get convective outflow velocity.

    Arguments
    ---------
    grid : flowx.Grid object
        Grid containing data.
    ivar : string
        Name of the velocity variable on the grid.

    Returns
    -------
    convvel : float
        Variable containing outflow velocity.

    """
    vel = grid.get_values(ivar)

    convvel = numpy.mean(vel[-1, :])

    return convvel


def update_outflow_bc(grid, ivar, dt, convvel=None):
    """Update the value of the velocity at the right boundary.

    The function uses a linear convective equation in the x-direction
    where the convective velocity is defined as the mean x-velocity
    along the right boundary.

    Parameters
    ----------
    grid : flowx.GridFaceX object
        The grid for the velocity.
    ivar : string
        Name of the variable in the Grid structure.
    dt : float
       Time-step size.
    convvel : float (optional)
        Convective velocity;
        default: None (will compute the convective velocity).

    """
    vel = grid.get_values(ivar)
    dx = grid.dx

    if convvel is None:
        convvel = get_convvel(grid, ivar)

    bc_val = grid.bc_val[ivar]
    bc_val[1] = vel[-1, :] - convvel * dt * (vel[-1, :] - vel[-2, :]) / dx
    grid.update_bc_val({ivar: bc_val})

    return
