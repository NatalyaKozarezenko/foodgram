import React from "react";
import { NavLink } from "react-router-dom";
import styles from "./style.module.css";
import cn from "classnames";

const LinkComponent = ({
  exact,
  href,
  title,
  className,
  activeClassName,
  ...rest
}) => {
  return (
    <NavLink
      exact={exact}
      activeClassName={activeClassName}
      className={cn(styles.link, className)}
      to={href}
      {...rest}
    >
      {title}
    </NavLink>
  );
};

export default LinkComponent;
